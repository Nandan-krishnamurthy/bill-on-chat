from app.agents.customer_agent import handle_customer_request


async def route_message(
    message: str,
    business_id: int,
):
    if "add customer" in message.lower():
        return await handle_customer_request(
            message,
            business_id,
        )

    return {
        "success": False,
        "message": "Unsupported command",
    }