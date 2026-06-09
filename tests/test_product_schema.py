from app.schemas.product import ProductCreate
from pydantic import ValidationError
import pytest


def test_product_schema_valid():
    product = ProductCreate(
        business_id=1,
        name="Surf Excel",
        hsn="34022090",
        sell_price=250,
        cost=180,
        gst_rate=18,
        stock=50,
        unit="pcs"
    )

    assert product.name == "Surf Excel"


def test_negative_sell_price():
    with pytest.raises(ValidationError):
        ProductCreate(
            business_id=1,
            name="Surf Excel",
            hsn="34022090",
            sell_price=-250,
            cost=180,
            gst_rate=18,
            stock=50,
            unit="pcs"
        )


def test_negative_stock():
    with pytest.raises(ValidationError):
        ProductCreate(
            business_id=1,
            name="Surf Excel",
            hsn="34022090",
            sell_price=250,
            cost=180,
            gst_rate=18,
            stock=-1,
            unit="pcs"
        )


def test_negative_low_stock_threshold():
    with pytest.raises(ValidationError):
        ProductCreate(
            business_id=1,
            name="Surf Excel",
            hsn="34022090",
            sell_price=250,
            cost=180,
            gst_rate=18,
            stock=50,
            low_stock_threshold=-5,
            unit="pcs"
        )


def test_invalid_gst_rate():
    with pytest.raises(ValidationError):
        ProductCreate(
            business_id=1,
            name="Surf Excel",
            hsn="34022090",
            sell_price=250,
            cost=180,
            gst_rate=50,
            stock=50,
            unit="pcs"
        )