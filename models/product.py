from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _get_utc_now() -> datetime:
    """Helper to return current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class Product:
    """Domain model representing a scraped product across e-commerce platforms.

    Attributes:
        name: The display title of the product.
        price: The numeric price of the item.
        currency: ISO 4217 currency code (e.g., 'THB', 'USD').
        platform: Name of the e-commerce platform (e.g., 'Shopee', 'Lazada').
        url: Direct product link or canonical URL.
        in_stock: Availability status of the item.
        scraped_at: Timestamp when the item was scraped (UTC).
    """

    name: str
    price: float
    currency: str
    platform: str
    url: str
    in_stock: bool
    scraped_at: datetime = field(default_factory=_get_utc_now)

    def __post_init__(self) -> None:
        """Validate domain model invariants upon instantiation."""
        if not self.name or not self.name.strip():
            raise ValueError("Product name cannot be empty.")
        if self.price < 0:
            raise ValueError(f"Product price cannot be negative: {self.price}")
        if not self.currency or len(self.currency.strip()) != 3:
            raise ValueError(f"Invalid currency code: {self.currency}. Must be 3-letter ISO code.")
        if not self.platform or not self.platform.strip():
            raise ValueError("Platform name cannot be empty.")

    def formatted_price(self) -> str:
        """Return a human-readable formatted price string with currency code."""
        return f"{self.currency.upper()} {self.price:,.2f}"

    def to_dict(self) -> dict[str, Any]:
        """Convert the domain model to a dictionary representation."""
        return {
            "name": self.name,
            "price": self.price,
            "currency": self.currency,
            "platform": self.platform,
            "url": self.url,
            "in_stock": self.in_stock,
            "scraped_at": self.scraped_at.isoformat(),
        }
