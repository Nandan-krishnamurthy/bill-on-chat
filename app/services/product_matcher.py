from sqlalchemy import select

from app.db.models.product import Product
from app.db.session import AsyncSessionLocal


async def find_product_candidates(
    business_id: int,
    search_term: str,
):
    """
    Find products using partial name matching.

    Example:
        surf ->
            Surf Excel 1kg
            Surf Excel 500g
            Surf Excel Matic
    """

    async with AsyncSessionLocal() as session:

        result = await session.execute(
            select(Product)
            .where(
                Product.business_id == business_id,
                Product.name.ilike(f"%{search_term}%"),
            )
            .order_by(Product.name)
        )

        return result.scalars().all()