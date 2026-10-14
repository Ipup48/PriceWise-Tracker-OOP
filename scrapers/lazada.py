from datetime import datetime, timezone
from typing import Any

from models.product import Product
from scrapers.base import BaseScraper


class MockLazadaScraper(BaseScraper):
    """Concrete scraper simulating data extraction from Lazada marketplace.

    Simulates Lazada's typical REST/Web API response structure where prices
    might be string floats (e.g., "11450.00"), stock is a boolean flag,
    and currencies could include international cross-border listings (e.g., USD or THB).
    """

    def __init__(self) -> None:
        self._platform_name: str = "Lazada"
        self._base_url: str = "https://www.lazada.co.th"

        # Realistic mock catalog stored as simulated Lazada API records
        self._catalog: list[dict[str, Any]] = [
            {
                "nid": "laz_8801",
                "title": "Sony WH-1000XM5 Premium Noise Cancelling Headphones",
                "sale_price": "11450.00",  # Cheaper than Shopee!
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/sony-wh-1000xm5-i8801.html",
            },
            {
                "nid": "laz_8802",
                "title": "Apple AirPods Pro (2nd Gen) with USB-C MagSafe Case",
                "sale_price": "219.00",  # Listed in USD (cross-border seller)
                "currency_code": "USD",
                "is_available": True,
                "sku_path": "products/apple-airpods-pro-2-i8802.html",
            },
            {
                "nid": "laz_8803",
                "title": "Logitech MX Master 3S Wireless Mouse Quiet Clicks",
                "sale_price": "3190.00",  # In stock on Lazada, out of stock on Shopee!
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/logitech-mx-master-3s-i8803.html",
            },
            {
                "nid": "laz_8804",
                "title": "Keychron K2 V2 Wireless Mechanical Keyboard Hot-Swappable",
                "sale_price": "2990.00",
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/keychron-k2-v2-i8804.html",
            },
            {
                "nid": "laz_8805",
                "title": "Samsung Galaxy Tab S9 128GB Wi-Fi Tablet",
                "sale_price": "24500.00",
                "currency_code": "THB",
                "is_available": True,
                "sku_path": "products/samsung-galaxy-tab-s9-i8805.html",
            },
            {
                "nid": "laz_8806",
                "title": "Bose QuietComfort 45 Bluetooth Wireless Headphones",
                "sale_price": "10800.00",
                "currency_code": "THB",
                "is_available": False,  # Out of stock
                "sku_path": "products/bose-qc-45-i8806.html",
            },
        ]

    @property
    def platform_name(self) -> str:
        """Return marketplace platform name."""
        return self._platform_name

    @property
    def base_url(self) -> str:
        """Return base URL of the marketplace."""
        return self._base_url

    def fetch(self, keyword: str) -> list[dict[str, Any]]:
        """Simulate fetching raw items matching keyword from Lazada API.

        Filters mock catalog records where the search tokens match product title.

        Args:
            keyword: Product search query.

        Returns:
            List of raw dictionaries resembling Lazada product search JSON.
        """
        search_terms = keyword.lower().split()
        results: list[dict[str, Any]] = []

        for item in self._catalog:
            title = item["title"].lower()
            if any(term in title for term in search_terms):
                results.append(dict(item))

        return results

    def parse(self, raw_data: list[dict[str, Any]]) -> list[Product]:
        """Convert raw Lazada records into standardized domain Product objects.

        Parses string numeric prices into floats and normalizes availability.

        Args:
            raw_data: List of raw Lazada items.

        Returns:
            List of domain `Product` instances.
        """
        products: list[Product] = []

        for raw_item in raw_data:
            try:
                price_val = float(raw_item.get("sale_price", 0.0))
            except (ValueError, TypeError):
                price_val = 0.0

            sku_path = raw_item.get("sku_path", "")
            currency = raw_item.get("currency_code", "THB")
            is_available = bool(raw_item.get("is_available", False))

            product = Product(
                name=raw_item.get("title", "Unknown Item"),
                price=round(price_val, 2),
                currency=currency,
                platform=self.platform_name,
                url=f"{self.base_url}/{sku_path}",
                in_stock=is_available,
                scraped_at=datetime.now(timezone.utc),
            )
            products.append(product)

        return products
