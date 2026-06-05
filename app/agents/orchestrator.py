from app.agents.customer_agent import handle_customer_request


async def route_message(message: str):
    if "add customer" in message.lower():
        return await handle_customer_request(message)

    return {
        "success": False,
        "message": "Unsupported command",
    }