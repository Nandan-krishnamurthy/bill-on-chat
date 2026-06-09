from typing import Optional

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    business_id: int

    name: str = Field(
        min_length=2,
        max_length=255
    )

    hsn: str = Field(
        min_length=4,
        max_length=8
    )

    sell_price: float = Field(
        gt=0
    )

    cost: Optional[float] = Field(
        default=None,
        ge=0
    )

    gst_rate: int = Field(
        ge=0,
        le=28
    )

    stock: int = Field(
        ge=0
    )

    low_stock_threshold: int = Field(
        default=5,
        ge=0
    )

    unit: str = Field(
        min_length=1,
        max_length=50
    )


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=255
    )

    hsn: Optional[str] = Field(
        default=None,
        min_length=4,
        max_length=8
    )

    sell_price: Optional[float] = Field(
        default=None,
        gt=0
    )

    cost: Optional[float] = Field(
        default=None,
        ge=0
    )

    gst_rate: Optional[int] = Field(
        default=None,
        ge=0,
        le=28
    )

    stock: Optional[int] = Field(
        default=None,
        ge=0
    )

    low_stock_threshold: Optional[int] = Field(
        default=None,
        ge=0
    )

    unit: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50
    )



   # Why these validations?
    #Price
    #gt=0

    #Prevents:

    #sell_price = 0
    #sell_price = -100
    #Stock
    ##ge=0

    #Prevents:

    #stock = -5
    #Threshold
    ##ge=0



    ##Prevents:

    #low_stock_threshold = -1
    #GST
    #0 <= gst_rate <= 28

    #Matches GST slabs from the project spec.