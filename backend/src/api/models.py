from datetime import datetime
from typing import Optional, List

from sqlalchemy import Integer, String, DateTime, Float, ForeignKey, Index, text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .db import Base


class Product(Base):
    """Product tracked by PriceSense."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True, unique=True)
    current_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_checked: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    # Relationships
    price_history: Mapped[List["PriceHistory"]] = relationship(
        "PriceHistory",
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    alerts: Mapped[List["Alert"]] = relationship(
        "Alert",
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        Index("ix_products_url", "url"),
        Index("ix_products_last_checked", "last_checked"),
    )


class PriceHistory(Base):
    """Historical price entries for a Product."""

    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    price: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), index=True
    )

    # Relationship
    product: Mapped[Product] = relationship("Product", back_populates="price_history")

    __table_args__ = (
        Index("ix_price_history_product_ts", "product_id", "timestamp"),
    )


class Alert(Base):
    """Alert generated for a Product when certain criteria are met."""

    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    price: Mapped[float] = mapped_column(Float, nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"), index=True
    )
    message: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Relationship
    product: Mapped[Product] = relationship("Product", back_populates="alerts")

    __table_args__ = (
        Index("ix_alerts_product_triggered", "product_id", "triggered_at"),
    )
