from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


# Shared base schemas
class ProductBase(BaseModel):
    name: str = Field(..., description="Display name of the product")
    url: Optional[str] = Field(None, description="Canonical URL to the product")
    current_price: Optional[float] = Field(None, description="Latest known price for the product")


class ProductCreate(ProductBase):
    """Payload to create a product."""
    name: str = Field(..., description="Product name")
    url: Optional[str] = Field(None, description="Product URL")
    current_price: Optional[float] = Field(None, description="Initial price if known")


class ProductUpdate(BaseModel):
    """Payload to update a product."""
    name: Optional[str] = Field(None, description="New product name")
    url: Optional[str] = Field(None, description="New product URL")
    current_price: Optional[float] = Field(None, description="Updated current price")


class PriceHistoryBase(BaseModel):
    price: float = Field(..., description="Recorded price value")
    timestamp: Optional[datetime] = Field(None, description="Timestamp when the price was recorded")


class PriceHistoryCreate(PriceHistoryBase):
    """Payload to create a price history entry."""
    pass


class AlertBase(BaseModel):
    price: float = Field(..., description="Price when the alert was triggered")
    triggered_at: Optional[datetime] = Field(None, description="When the alert was triggered")
    message: Optional[str] = Field(None, description="Details about the alert")


class AlertCreate(AlertBase):
    """Payload to create an alert."""
    pass


# Read models
class PriceHistoryRead(PriceHistoryBase):
    id: int = Field(..., description="Unique identifier of the price history row")
    product_id: int = Field(..., description="Product ID this entry belongs to")

    class Config:
        from_attributes = True


class AlertRead(AlertBase):
    id: int = Field(..., description="Unique identifier of the alert")
    product_id: int = Field(..., description="Product ID this alert is for")

    class Config:
        from_attributes = True


class ProductRead(ProductBase):
    id: int = Field(..., description="Unique identifier of the product")
    last_checked: datetime = Field(..., description="When the product price was last checked")
    price_history: List[PriceHistoryRead] = Field(default_factory=list, description="Historical price data")
    alerts: List[AlertRead] = Field(default_factory=list, description="Associated alerts")

    class Config:
        from_attributes = True
