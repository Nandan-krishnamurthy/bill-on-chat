from app.schemas.customer import CustomerCreate
from app.tools.customer_tools import create_customer
from app.services.llm_tools import llm_customer_intent


async def handle_customer_request(
    message: str,
    business_id: int,
):
    """
    Customer Agent - LLM-driven tool selection.
    
    The LLM understands natural language variations and decides
    whether to create a customer or handle other requests.
    
    Examples:
    - "Add customer Ramesh 9876543210"
    - "Create new customer named Priya, phone 8765432109"
    - "I need to add a customer: Suresh (9988776655)"
    """
    
    # Use LLM to understand intent and extract parameters
    intent = await llm_customer_intent(message, business_id)
    
    if intent["tool"] == "create_customer":
        params = intent["parameters"]
        
        # Validate required fields
        if not params.get("name") or not params.get("phone"):
            return {
                "success": False,
                "message": "Please provide both customer name and 10-digit phone number.",
            }
        
        # Validate phone number format
        phone = str(params.get("phone", "")).strip()
        if not phone.isdigit() or len(phone) != 10:
            return {
                "success": False,
                "message": "Phone number must be exactly 10 digits.",
            }
        
        # Create customer
        customer = CustomerCreate(
            business_id=business_id,
            name=params.get("name", "").strip(),
            phone=phone,
            state=params.get("state", "Karnataka"),
        )
        
        return await create_customer(customer)
    
    else:
        # Not a customer creation request
        return {
            "success": False,
            "message": "I didn't understand that request. Please use natural language like: 'Add customer Ramesh 9876543210'",
        }