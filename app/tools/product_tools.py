from sqlalchemy import select, func

from app.db.models.product import Product
from app.db.session import AsyncSessionLocal
from app.schemas.product import ProductCreate, ProductUpdate


async def create_product(product_data: ProductCreate) -> dict:
    """
    Create a product if one does not already exist
    for the same business_id + product name combination.
    """

    async with AsyncSessionLocal() as session:

        # Check duplicate product within the same business
        result = await session.execute(
            select(Product).where(
                Product.business_id == product_data.business_id,
                func.lower(Product.name) == product_data.name.lower(),
            )
        )

        existing_product = result.scalar_one_or_none()

        if existing_product:
            return {
                "success": False,
                "message": f"Product {existing_product.name} already exists",
                "product_id": existing_product.id,
            }

        # Create new product
        product = Product(
            business_id=product_data.business_id,
            name=product_data.name,
            hsn=product_data.hsn,
            sell_price=product_data.sell_price,
            cost=product_data.cost,
            gst_rate=product_data.gst_rate,
            stock=product_data.stock,
            low_stock_threshold=product_data.low_stock_threshold,
            unit=product_data.unit,
        )

        session.add(product)

        await session.commit()

        await session.refresh(product)

        return {
            "success": True,
            "product_id": product.id,
            "message": f"Product {product.name} created successfully",
        }


async def update_product(
    business_id: int,
    product_name: str,
    product_data: ProductUpdate,
) -> dict:
    """
    Update an existing product identified by
    business_id + product name.
    """

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(Product).where(
                Product.business_id == business_id,
                func.lower(Product.name) == product_name.lower(),
            )
        )

        product = result.scalar_one_or_none()

        if not product:
            return {
                "success": False,
                "message": f"Product {product_name} not found",
            }

        update_data = product_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(product, field, value)

        await session.commit()

        await session.refresh(product)

        return {
            "success": True,
            "product_id": product.id,
            "message": f"Product {product.name} updated successfully",
        }