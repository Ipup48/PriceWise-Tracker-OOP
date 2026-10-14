from datetime import datetime, timezone
from typing import Any

from models.product import Product
from scrapers.base import BaseScraper


class MockShopeeScraper(BaseScraper):
    """Concrete scraper simulating data extraction from Shopee marketplace.

    Simulates Shopee's typical JSON API payload structure where prices might be
    represented in cents/satang (e.g., multiplied by 100 or 100,000) and items
    have stock counts and unique item IDs.
    """

    def __init__(self) -> None:
        self._platform_name: str = "Shopee"
        self._base_url: str = "https://shopee.co.th"

        # Realistic mock catalog stored as simulated Shopee API records
        self._catalog: list[dict[str, Any]] = [
            {
                "item_id": "sp_101",
                "item_name": "Sony WH-1000XM5 Wireless Noise-Canceling Headphones (Black)",
                "price_satang": 1199000,  # 11,990.00 THB
                "currency": "THB",
                "stock_count": 14,
                "url_slug": "sony-wh-1000xm5-sp101",
            },
            {
                "item_id": "sp_102",
                "item_name": "Apple AirPods Pro (2nd Generation) with MagSafe Case (USB-C)",
                "price_satang": 789000,  # 7,890.00 THB
                "currency": "THB",
                "stock_count": 8,
                "url_slug": "apple-airpods-pro-2-sp102",
            },
            {
                "item_id": "sp_103",
                "item_name": "Logitech MX Master 3S Wireless Performance Mouse (Graphite)",
                "price_satang": 339000,  # 3,390.00 THB
                "currency": "THB",
                "stock_count": 0,  # Out of stock
                "url_slug": "logitech-mx-master-3s-sp103",
            },
            {
                "item_id": "sp_104",
                "item_name": "Keychron K2 V2 Wireless Mechanical Keyboard (Gateron Brown)",
                "price_satang": 285000,  # 2,850.00 THB
                "currency": "THB",
                "stock_count": 5,
                "url_slug": "keychron-k2-v2-sp104",
            },
            {
                "item_id": "sp_105",
                "item_name": "Samsung Galaxy Tab S9 128GB Wi-Fi (Graphite)",
                "price_satang": 2490000,  # 24,900.00 THB
                "currency": "THB",
                "stock_count": 3,
                "url_slug": "samsung-galaxy-tab-s9-sp105",
            },
            {
                "item_id": "sp_106",
                "item_name": "Bose QuietComfort 45 Headphones",
                "price_satang": 1050000,  # 10,500.00 THB
                "currency": "THB",
                "stock_count": 2,
                "url_slug": "bose-qc-45-sp106",
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
        """Simulate fetching raw items matching keyword from Shopee API.

        Filters mock catalog records where the search tokens match item name.

        Args:
            keyword: Product search query.

        Returns:
            List of raw dictionaries resembling Shopee JSON search results.
        """
        search_terms = keyword.lower().split()
        results: list[dict[str, Any]] = []

        for item in self._catalog:
            item_name = item["item_name"].lower()
            if any(term in item_name for term in search_terms):
                # Return deep-enough copy to simulate fresh API payload
                results.append(dict(item))

        return results

    def parse(self, raw_data: list[dict[str, Any]]) -> list[Product]:
        """Convert raw Shopee records into standardized domain Product objects.

        Converts satang integers to decimal float prices and builds platform URLs.

        Args:
            raw_data: List of raw Shopee items.

        Returns:
            List of domain `Product` instances.
        """
        products: list[Product] = []

        for raw_item in raw_data:
            price_satang = raw_item.get("price_satang", 0)
            price_thb = round(price_satang / 100.0, 2)
            url_slug = raw_item.get("url_slug", "")
            stock_count = raw_item.get("stock_count", 0)

            product = Product(
                name=raw_item.get("item_name", "Unknown Item"),
                price=price_thb,
                currency=raw_item.get("currency", "THB"),
                platform=self.platform_name,
                url=f"{self.base_url}/product/{url_slug}",
                in_stock=stock_count > 0,
                scraped_at=datetime.now(timezone.utc),
            )
            products.append(product)

        return products
