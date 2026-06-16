"""
Product Agent - LLM-driven tool selection with state-based disambiguation.

The LLM understands natural language variations for creating and updating products.
For updates, if multiple products match, the system asks the user to disambiguate
using numeric selection (1, 2, 3...).
"""

import re
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.product_matcher import find_product_candidates
from app.tools.product_tools import create_product, update_product
from app.services.llm_tools import llm_product_intent


async def handle_product_request(
    message: str,
    business_id: int,
    state: dict,
):
    """
    Product Agent - LLM-driven tool selection.
    
    Examples:
    - Create: "Add product Surf Excel 1kg HSN 3402 Rs 250 GST 18% 50 in stock"
    - Create: "I want to add a product: Matic 1kg, HSN 3402, price 300, GST 18%, stock 100"
    - Update: "Update product Surf stock to 100"
    - Update: "Set Matic quantity to 250"
    - Disambiguate: "1" (select first product from list)
    """

    # Handle candidate selection (numeric disambiguation)
    if state.get("awaiting_product_selection"):
        selection_match = re.match(r"^\s*(\d+)\s*$", message)

        if selection_match:
            selection_num = int(selection_match.group(1))
            candidates = state.get("pending_candidates", [])

            # Validate selection range
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
        else:
            # User sent non-numeric input while awaiting selection
            return {
                "success": False,
                "message": "Please select a product number from the list above.",
            }

    # Use LLM to understand product intent
    intent = await llm_product_intent(message, business_id)

    if intent["tool"] == "create_product":
        params = intent["parameters"]
        
        # Validate required fields
        required = ["name", "hsn", "sell_price", "gst_rate", "stock"]
        if not all(params.get(f) for f in required):
            return {
                "success": False,
                "message": "To create a product, please provide: name, HSN, price, GST rate, and stock quantity.",
            }
        
        try:
            # Convert types
            sell_price = float(params["sell_price"])
            gst_rate = int(params["gst_rate"])
            stock = int(params["stock"])
            
            # Validate ranges
            if gst_rate < 0 or gst_rate > 28:
                return {
                    "success": False,
                    "message": "GST rate must be between 0 and 28.",
                }
            
            if stock < 0:
                return {
                    "success": False,
                    "message": "Stock quantity cannot be negative.",
                }
            
            if sell_price < 0:
                return {
                    "success": False,
                    "message": "Price cannot be negative.",
                }
            
            name = params["name"].strip()
            state["last_product_name"] = name

            product = ProductCreate(
                business_id=business_id,
                name=name,
                hsn=params["hsn"].strip(),
                sell_price=sell_price,
                cost=None,
                gst_rate=gst_rate,
                stock=stock,
                low_stock_threshold=5,
                unit="pcs",
            )

            return await create_product(product)
        
        except (ValueError, TypeError) as e:
            return {
                "success": False,
                "message": f"Invalid product data: {str(e)}",
            }

    elif intent["tool"] == "update_stock":
        params = intent["parameters"]
        
        # Validate required fields
        if not params.get("product_name") or "stock" not in params:
            return {
                "success": False,
                "message": "Please specify the product name and new stock quantity.",
            }
        
        try:
            search_term = params.get("product_name", "").strip()
            stock = int(params.get("stock", 0))
            
            if stock < 0:
                return {
                    "success": False,
                    "message": "Stock quantity cannot be negative.",
                }
            
            # Find matching products
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
                # Single match - update directly
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

            # Multiple matches - ask user to disambiguate
            state["awaiting_product_selection"] = True
            state["pending_candidates"] = [
                {"name": candidate.name} for candidate in candidates
            ]
            state["pending_stock"] = stock

            # Build selection prompt with proper formatting
            candidate_list = "\n".join(
                [f"{i + 1}. {candidate.name}" for i, candidate in enumerate(candidates)]
            )

            return {
                "success": False,
                "message": f"Multiple products found matching '{search_term}'.\n\n{candidate_list}\n\nPlease select a product number.",
            }
        
        except (ValueError, TypeError) as e:
            return {
                "success": False,
                "message": f"Invalid input: {str(e)}",
            }

    elif intent["tool"] == "unknown":
        return {
            "success": False,
            "message": "I didn't understand that product request. You can create products or update stock.",
        }
    
    else:
        return {
            "success": False,
            "message": "Unknown product operation.",
        }
