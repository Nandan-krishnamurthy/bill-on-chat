from pydantic import BaseModel, Field
from typing import Optional


class CustomerCreate(BaseModel):
    business_id: int

    name: str = Field(
        min_length=2,
        max_length=100
    )

    phone: str = Field(
        min_length=10,
        max_length=15
    )

    gstin: Optional[str] = None
    state: Optional[str] = None
    address: Optional[str] = None