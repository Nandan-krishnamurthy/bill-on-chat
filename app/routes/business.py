from fastapi import APIRouter
from sqlalchemy import select

from app.db.models.business import Business
from app.db.session import AsyncSessionLocal

router = APIRouter()


@router.get("/businesses")
async def list_businesses():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Business.id, Business.name)
            .order_by(Business.name)
        )

        businesses = result.all()

        return [
            {
                "id": business.id,
                "name": business.name,
            }
            for business in businesses
        ]