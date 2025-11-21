from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Body, status, Response
from sqlalchemy.orm import Session

from .db import get_db
from . import models, schemas
from .services import PricingService, maybe_create_alert

products_router = APIRouter(prefix="/products", tags=["products"])
alerts_router = APIRouter(prefix="/alerts", tags=["alerts"])
jobs_router = APIRouter(prefix="/jobs", tags=["jobs"])

pricing_service = PricingService()


# PUBLIC_INTERFACE
@products_router.get(
    "",
    response_model=List[schemas.ProductRead],
    summary="List products",
    description="Returns all tracked products with nested price history and alerts.",
)
def list_products(db: Session = Depends(get_db)) -> List[schemas.ProductRead]:
    """List all products."""
    products = db.query(models.Product).all()
    return products


# PUBLIC_INTERFACE
@products_router.post(
    "",
    response_model=schemas.ProductRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create product",
    description="Create a new product with optional initial current_price.",
)
def create_product(payload: schemas.ProductCreate, db: Session = Depends(get_db)) -> schemas.ProductRead:
    """Create a product."""
    product = models.Product(
        name=payload.name,
        url=payload.url,
        current_price=payload.current_price,
        last_checked=datetime.utcnow(),
    )
    db.add(product)
    db.flush()  # get id for relations

    # If initial price provided, add history
    if payload.current_price is not None:
        ph = models.PriceHistory(product_id=product.id, price=payload.current_price, timestamp=datetime.utcnow())
        db.add(ph)

    db.commit()
    db.refresh(product)
    return product


def _get_product_or_404(db: Session, product_id: int) -> models.Product:
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# PUBLIC_INTERFACE
@products_router.get(
    "/{product_id}",
    response_model=schemas.ProductRead,
    summary="Get product",
    description="Get a product by ID including price history and alerts.",
)
def get_product(
    product_id: int = Path(..., description="Product ID"),
    db: Session = Depends(get_db),
) -> schemas.ProductRead:
    """Get a product by ID."""
    return _get_product_or_404(db, product_id)


# PUBLIC_INTERFACE
@products_router.put(
    "/{product_id}",
    response_model=schemas.ProductRead,
    summary="Update product (replace fields)",
    description="Update a product by replacing provided fields.",
)
def update_product_put(
    product_id: int = Path(..., description="Product ID"),
    payload: schemas.ProductUpdate = Body(...),
    db: Session = Depends(get_db),
) -> schemas.ProductRead:
    """Update a product with PUT semantics."""
    product = _get_product_or_404(db, product_id)

    # Replace provided fields (PUT here behaves same as PATCH with provided fields)
    for field in ["name", "url", "current_price"]:
        value = getattr(payload, field)
        if value is not None:
            setattr(product, field, value)

    product.last_checked = datetime.utcnow()
    db.commit()
    db.refresh(product)
    return product


# PUBLIC_INTERFACE
@products_router.patch(
    "/{product_id}",
    response_model=schemas.ProductRead,
    summary="Patch product (partial update)",
    description="Partially update a product.",
)
def update_product_patch(
    product_id: int = Path(..., description="Product ID"),
    payload: schemas.ProductUpdate = Body(...),
    db: Session = Depends(get_db),
) -> schemas.ProductRead:
    """Patch a product."""
    return update_product_put(product_id, payload, db)  # reuse logic


# PUBLIC_INTERFACE
@products_router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    response_class=Response,
    summary="Delete product",
    description="Delete a product and associated price history and alerts.",
)
def delete_product(
    product_id: int = Path(..., description="Product ID"),
    db: Session = Depends(get_db),
) -> None:
    """Delete a product.

    Note: 204 No Content must not return a response body.
    """
    product = _get_product_or_404(db, product_id)
    db.delete(product)
    db.commit()
    # Do not return anything; 204 responses must have no body.


# PUBLIC_INTERFACE
@products_router.get(
    "/{product_id}/history",
    response_model=List[schemas.PriceHistoryRead],
    summary="Get product price history",
    description="Return all price history entries for the given product ordered by timestamp ascending.",
)
def get_price_history(
    product_id: int = Path(..., description="Product ID"),
    db: Session = Depends(get_db),
) -> List[schemas.PriceHistoryRead]:
    """Get price history for a product."""
    _ = _get_product_or_404(db, product_id)
    history = (
        db.query(models.PriceHistory)
        .filter(models.PriceHistory.product_id == product_id)
        .order_by(models.PriceHistory.timestamp.asc())
        .all()
    )
    return history


# PUBLIC_INTERFACE
@alerts_router.get(
    "",
    response_model=List[schemas.AlertRead],
    summary="List alerts",
    description="Return all alerts ordered by triggered_at descending.",
)
def list_alerts(db: Session = Depends(get_db)) -> List[schemas.AlertRead]:
    """List all alerts."""
    alerts = db.query(models.Alert).order_by(models.Alert.triggered_at.desc()).all()
    return alerts


# PUBLIC_INTERFACE
@jobs_router.post(
    "/fetch-latest",
    summary="Fetch latest prices",
    description="Fetch latest prices for all products, append to price history when changed, and create alerts if new lowest price detected.",
)
def fetch_latest_prices_job(db: Session = Depends(get_db)) -> dict:
    """Fetch latest prices and update database.

    For each product:
    - Fetch latest price using PricingService stub
    - If the price differs from current, update product.current_price, add PriceHistory
    - Evaluate alert heuristic and create alert if criteria met
    """
    products: List[models.Product] = db.query(models.Product).all()
    updated = 0
    alerts_created = 0

    for p in products:
        latest = pricing_service.fetch_latest_price(p)
        if latest is None:
            continue

        if p.current_price is None or float(latest) != float(p.current_price):
            p.current_price = float(latest)
            p.last_checked = datetime.utcnow()
            db.add(models.PriceHistory(product_id=p.id, price=p.current_price, timestamp=datetime.utcnow()))
            alert = maybe_create_alert(db, p, p.current_price)
            if alert is not None:
                alerts_created += 1
            updated += 1

    db.commit()
    return {"processed": len(products), "updated": updated, "alerts_created": alerts_created}
