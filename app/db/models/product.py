from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, ForeignKey, Numeric, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    hsn: Mapped[str] = mapped_column(String(8))
    sell_price: Mapped[float] = mapped_column(Numeric(12, 2))
    cost: Mapped[float] = mapped_column(Numeric(12, 2))
    gst_rate: Mapped[float] = mapped_column(Numeric(5, 2))
    stock: Mapped[int] = mapped_column(Integer)
    unit: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
