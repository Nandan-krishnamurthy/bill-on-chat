import re

from app.schemas.product import ProductCreate, ProductUpdate
from app.tools.product_tools import create_product, update_product


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
    """

    create_match = re.search(
        r"add product\s+(.+?)\s+hsn\s+(\d{4,8})\s+rs\s+(\d+(?:\.\d+)?)\s+gst\s+(\d{1,2})%\s+(\d+)\s+in stock",
        message,
        re.IGNORECASE,
    )

    if create_match:

        name = create_match.group(1).strip()

        # Day 12 - Remember last product
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

    update_match = re.search(
        r"update product\s+(.+?)\s+stock\s+to\s+(\d+)",
        message,
        re.IGNORECASE,
    )

    if update_match:

        product_name = update_match.group(1).strip()

        # Day 12 - Remember last product
        state["last_product_name"] = product_name

        stock = int(update_match.group(2))

        product_update = ProductUpdate(
            stock=stock,
        )

        return await update_product(
            business_id=business_id,
            product_name=product_name,
            product_data=product_update,
        )

    # Day 12 - Memory-based update
    memory_update_match = re.search(
        r"update stock to\s+(\d+)",
        message,
        re.IGNORECASE,
    )

    if memory_update_match:

        product_name = state.get(
            "last_product_name"
        )

        if not product_name:
            return {
                "success": False,
                "message": (
                    "No recent product found. "
                    "Please specify the product name."
                ),
            }

        stock = int(
            memory_update_match.group(1)
        )

        product_update = ProductUpdate(
            stock=stock,
        )

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