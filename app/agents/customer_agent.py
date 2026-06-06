import re

from app.schemas.customer import CustomerCreate
from app.tools.customer_tools import create_customer


async def handle_customer_request(
    message: str,
    business_id: int,
 ):
    """
    Example:
    Add customer Ramesh 9876543210
    """

    match = re.search(
        r"add customer\s+(.+?)\s+(\d{10})",
        message,
        re.IGNORECASE,
    )

    if not match:
        return {
            "success": False,
            "message": "Invalid customer format",
        }

    name = match.group(1).strip()
    phone = match.group(2)

    customer = CustomerCreate(
        business_id=business_id,  
        name=name,
        phone=phone,
        state="Karnataka",
    )

    return await create_customer(customer)