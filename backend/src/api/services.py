from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from . import models


class PricingService:
    """Stub pricing service that simulates fetching latest price from a URL or heuristic."""

    # PUBLIC_INTERFACE
    def fetch_latest_price(self, product: models.Product) -> Optional[float]:
        """Fetch the latest price for a product.

        This stub implementation generates a deterministic pseudo-price based on product id and current time.
        Replace with real scraping/API integration in production.

        Returns:
            Optional[float]: A price value or None if not determinable.
        """
        # If product has a URL we could do domain-specific logic. For stub, derive a value.
        base = (product.id or 1) * 1.11
        # Keep result bounded for demo purposes
        minute_factor = (datetime.utcnow().minute % 10) * 0.25
        computed = round((product.current_price or 50.0) * (0.98 + (minute_factor / 100.0)), 2)
        # Blend with base to simulate drift
        price = round((computed + base) / 2.0, 2)
        return price


def maybe_create_alert(db: Session, product: models.Product, new_price: float) -> Optional[models.Alert]:
    """Evaluate alert criteria and create alert if a significant drop is detected.

    Current heuristic:
    - Create an alert if the new price is the lowest in the recorded history (including current).

    Returns:
        models.Alert | None: Created alert if any, else None.
    """
    # Determine historical minimum
    history_prices: List[float] = [ph.price for ph in product.price_history]
    if product.current_price is not None:
        history_prices.append(product.current_price)

    if not history_prices or new_price < min(history_prices):
        alert = models.Alert(
            product_id=product.id,
            price=new_price,
            message=f"New lowest price detected: {new_price}",
        )
        db.add(alert)
        db.flush()  # Assign id
        return alert

    return None
