from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Numeric, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)

    business_id: Mapped[int] = mapped_column(
        ForeignKey("businesses.id"),
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    hsn: Mapped[str] = mapped_column(
        String(8),
        nullable=False,
    )

    sell_price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    cost: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    gst_rate: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    stock: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    low_stock_threshold: Mapped[int] = mapped_column(
        Integer,
        default=5,
        nullable=False,
    )

    unit: Mapped[str] = mapped_column(
        String(50),
        default="pcs",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )