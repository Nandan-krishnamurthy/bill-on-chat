from sqlalchemy import select

from app.db.models.customer import Customer
from app.db.session import AsyncSessionLocal
from app.schemas.customer import CustomerCreate


async def create_customer(customer_data: CustomerCreate) -> dict:
    """
    Create a customer if one does not already exist
    for the same business_id + phone combination.
    """

    async with AsyncSessionLocal() as session:

        # Check duplicate customer
        result = await session.execute(
            select(Customer).where(
                Customer.business_id == customer_data.business_id,
                Customer.phone == customer_data.phone,
            )
        )

        existing_customer = result.scalar_one_or_none()

        if existing_customer:
            return {
                "success": False,
                "message": "Customer already exists",
                "customer_id": existing_customer.id,
            }

        # Create new customer
        customer = Customer(
            business_id=customer_data.business_id,
            name=customer_data.name,
            phone=customer_data.phone,
            gstin=customer_data.gstin,
            state=customer_data.state,
            address=customer_data.address,
        )

        session.add(customer)

        await session.commit()

        await session.refresh(customer)

        return {
            "success": True,
            "customer_id": customer.id,
            "message": f"Customer {customer.name} created successfully",
        }