import re

from app.schemas.product import ProductCreate, ProductUpdate
from app.services.product_matcher import (
    find_product_candidates,
)
from app.tools.product_tools import (
    create_product,
    update_product,
)


async def handle_product_request(
    message: str,
    business_id: int,
    state: dict,
):
    """
    Product Agent

    Handles owner-mode product management requests.

    Supported commands:

    Create Product:
    Add product Surf Excel 1kg HSN 3402 Rs 250 GST 18% 50 in stock

    Update Stock:
    Update product Surf Excel 1kg stock to 100

    Memory-based Update:
    Update stock to 100

    Candidate Disambiguation:
    When multiple products match, user selects by number (1, 2, 3, etc.)
    """

    # Day 13: Handle candidate selection
    if state.get("awaiting_product_selection"):
        # Check if message is a valid selection number
        selection_match = re.match(r"^\s*(\d+)\s*$", message)

        if selection_match:
            selection_num = int(selection_match.group(1))
            candidates = state.get("pending_candidates", [])

            # Validate selection range (1-indexed for user, 0-indexed internally)
            if selection_num < 1 or selection_num > len(candidates):
                return {
                    "success": False,
                    "message": "Invalid selection. Please choose one of the listed product numbers.",
                }

            # Get selected candidate and perform update
            selected_candidate = candidates[selection_num - 1]
            product_name = selected_candidate.get("name")
            stock = state.get("pending_stock")

            product_update = ProductUpdate(stock=stock)

            result = await update_product(
                business_id=business_id,
                product_name=product_name,
                product_data=product_update,
            )

            if result["success"]:
                state["last_product_name"] = product_name

            # Clear selection state
            state["awaiting_product_selection"] = False
            state["pending_candidates"] = []
            state["pending_stock"] = None

            return result

    # Create Product
    create_match = re.search(
        r"add product\s+(.+?)\s+hsn\s+(\d{4,8})\s+rs\s+(\d+(?:\.\d+)?)\s+gst\s+(\d{1,2})%\s+(\d+)\s+in stock",
        message,
        re.IGNORECASE,
    )

    if create_match:
        name = create_match.group(1).strip()
        state["last_product_name"] = name

        hsn = create_match.group(2)
        sell_price = float(create_match.group(3))
        gst_rate = int(create_match.group(4))
        stock = int(create_match.group(5))

        product = ProductCreate(
            business_id=business_id,
            name=name,
            hsn=hsn,
            sell_price=sell_price,
            cost=None,
            gst_rate=gst_rate,
            stock=stock,
            low_stock_threshold=5,
            unit="pcs",
        )

        return await create_product(product)

    # Update Product with Fuzzy Lookup
    update_match = re.search(
        r"update product\s+(.+?)\s+stock\s+to\s+(\d+)",
        message,
        re.IGNORECASE,
    )

    if update_match:
        search_term = update_match.group(1).strip()
        stock = int(update_match.group(2))

        candidates = await find_product_candidates(
            business_id=business_id,
            search_term=search_term,
        )

        if len(candidates) == 0:
            return {
                "success": False,
                "message": f"No product found matching '{search_term}'.",
            }

        if len(candidates) == 1:
            product_name = candidates[0].name

            product_update = ProductUpdate(stock=stock)

            result = await update_product(
                business_id=business_id,
                product_name=product_name,
                product_data=product_update,
            )

            if result["success"]:
                state["last_product_name"] = product_name

            return result

        # Multiple candidates found: store in state and ask user to select
        state["awaiting_product_selection"] = True
        state["pending_candidates"] = [
            {"name": candidate.name} for candidate in candidates
        ]
        state["pending_stock"] = stock

        # Build selection prompt
        candidate_list = "\n".join(
            [f"{i + 1}. {candidate.name}" for i, candidate in enumerate(candidates)]
        )

        return {
            "success": False,
            "message": f"Multiple products found matching '{search_term}'.\n\n{candidate_list}\n\nPlease select a product number.",
        }

    # Memory-based Update (from conversation state)
    memory_update_match = re.search(
        r"update stock to\s+(\d+)",
        message,
        re.IGNORECASE,
    )

    if memory_update_match:
        product_name = state.get("last_product_name")

        if not product_name:
            return {
                "success": False,
                "message": (
                    "No recent product found. "
                    "Please specify the product name."
                ),
            }

        stock = int(memory_update_match.group(1))

        product_update = ProductUpdate(stock=stock)

        return await update_product(
            business_id=business_id,
            product_name=product_name,
            product_data=product_update,
        )

    return {
        "success": False,
        "message": (
            "Invalid product format. "
            "Example: Add product Surf Excel 1kg "
            "HSN 3402 Rs 250 GST 18% 50 in stock"
        ),
    }