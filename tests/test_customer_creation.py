from app.schemas.customer import CustomerCreate
from pydantic import ValidationError
import pytest


def test_customer_schema_valid():
    customer = CustomerCreate(
        business_id=1,
        name="Ramesh",
        phone="9876543210"
    )

    assert customer.name == "Ramesh"


def test_invalid_phone():
    with pytest.raises(ValidationError):
        CustomerCreate(
            business_id=1,
            name="Ramesh",
            phone="123"
        )