from app.agents.customer_agent import handle_customer_request
from app.agents.product_agent import handle_product_request


async def route_message(
    message: str,
    business_id: int,
    state: dict,
):
    """
    Route incoming owner-mode messages
    to the appropriate specialist agent.
    """

    message_lower = message.lower()

    if "add customer" in message_lower:
        return await handle_customer_request(
            message,
            business_id,
        )

    if (
        "add product" in message_lower
        or "update product" in message_lower
        or "update stock" in message_lower
    ):
        return await handle_product_request(
            message,
            business_id,
            state,
        )

    return {
        "success": False,
        "message": "Unsupported command",
    }