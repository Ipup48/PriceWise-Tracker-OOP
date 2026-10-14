from typing import Any
import pytest

from models.product import Product
from scrapers.base import BaseScraper
from scrapers.lazada import MockLazadaScraper
from scrapers.shopee import MockShopeeScraper


class DummyTrackingScraper(BaseScraper):
    """Test double scraper to verify Template Method lifecycle execution order."""

    def __init__(self) -> None:
        self.call_log: list[str] = []

    @property
    def platform_name(self) -> str:
        return "DummyPlatform"

    @property
    def base_url(self) -> str:
        return "https://dummy.example.com"

    def fetch(self, keyword: str) -> list[dict[str, Any]]:
        self.call_log.append("fetch")
        return [
            {"name": f"{keyword} Item A", "price": 100.0, "valid": True},
            {"name": f"{keyword} Item B (Invalid Price)", "price": -50.0, "valid": True},
            {"name": "", "price": 200.0, "valid": False},
        ]

    def parse(self, raw_data: list[dict[str, Any]]) -> list[Product]:
        self.call_log.append("parse")
        parsed: list[Product] = []
        for item in raw_data:
            try:
                prod = Product(
                    name=item["name"],
                    price=item["price"],
                    currency="THB",
                    platform=self.platform_name,
                    url=f"{self.base_url}/item",
                    in_stock=True,
                )
                parsed.append(prod)
            except ValueError:
                # If domain invariants reject it early (e.g. empty name or negative price),
                # domain constructor throws ValueError
                pass
        return parsed

    def validate(self, products: list[Product]) -> list[Product]:
        self.call_log.append("validate")
        return super().validate(products)


def test_base_scraper_template_method_lifecycle() -> None:
    """Verify that scrape() executes fetch -> parse -> validate in exact order."""
    scraper = DummyTrackingScraper()
    results = scraper.scrape("TestQuery")

    assert scraper.call_log == ["fetch", "parse", "validate"]
    assert len(results) == 1
    assert results[0].name == "TestQuery Item A"
    assert results[0].price == 100.0


def test_base_scraper_validation_filters_invalid_items() -> None:
    """Test that BaseScraper.validate filters out corrupt, non-product or invalid objects."""
    scraper = DummyTrackingScraper()

    # Create dummy objects
    valid_prod = Product(
        name="Valid",
        price=50.0,
        currency="THB",
        platform="Dummy",
        url="https://dummy.com/1",
        in_stock=True,
    )

    # Subclass with custom parser to test validate directly
    class TestableScraper(BaseScraper):
        @property
        def platform_name(self) -> str:
            return "Test"

        @property
        def base_url(self) -> str:
            return "https://test.com"

        def fetch(self, keyword: str) -> list[dict[str, Any]]:
            return []

        def parse(self, raw_data: list[dict[str, Any]]) -> list[Product]:
            return []

    test_scraper = TestableScraper()
    # Pass mixed items: valid, non-Product objects
    filtered = test_scraper.validate([valid_prod, "not-a-product"])  # type: ignore[list-item]

    assert len(filtered) == 1
    assert filtered[0].name == "Valid"


def test_shopee_scraper_fetch_and_parse() -> None:
    """Test MockShopeeScraper parsing and pricing conversions."""
    scraper = MockShopeeScraper()
    assert scraper.platform_name == "Shopee"
    assert "shopee.co.th" in scraper.base_url

    results = scraper.scrape("Sony")
    assert len(results) >= 1

    sony_item = next((p for p in results if "Sony" in p.name), None)
    assert sony_item is not None
    assert sony_item.price == 11990.00  # Converted from 1199000 satang
    assert sony_item.currency == "THB"
    assert sony_item.in_stock is True
    assert "shopee.co.th/product/" in sony_item.url


def test_shopee_scraper_out_of_stock_item() -> None:
    """Test MockShopeeScraper properly handles out-of-stock items."""
    scraper = MockShopeeScraper()
    results = scraper.scrape("Logitech")

    assert len(results) >= 1
    logitech = next((p for p in results if "Logitech" in p.name), None)
    assert logitech is not None
    assert logitech.in_stock is False
    assert logitech.price == 3390.00


def test_lazada_scraper_fetch_and_parse() -> None:
    """Test MockLazadaScraper parsing string prices and URLs."""
    scraper = MockLazadaScraper()
    assert scraper.platform_name == "Lazada"
    assert "lazada.co.th" in scraper.base_url

    results = scraper.scrape("Sony")
    assert len(results) >= 1

    sony_item = next((p for p in results if "Sony" in p.name), None)
    assert sony_item is not None
    assert sony_item.price == 11450.00
    assert sony_item.currency == "THB"
    assert sony_item.in_stock is True
    assert "lazada.co.th/products/" in sony_item.url


def test_lazada_scraper_currency_variation() -> None:
    """Test MockLazadaScraper returns items with USD currency."""
    scraper = MockLazadaScraper()
    results = scraper.scrape("AirPods")

    assert len(results) >= 1
    airpods = next((p for p in results if "AirPods" in p.name), None)
    assert airpods is not None
    assert airpods.currency == "USD"
    assert airpods.price == 219.00
    assert airpods.in_stock is True


def test_scraper_no_match() -> None:
    """Test scraper behavior when keyword returns zero matches."""
    shopee = MockShopeeScraper()
    lazada = MockLazadaScraper()

    assert shopee.scrape("NonExistentItemXYZ123") == []
    assert lazada.scrape("NonExistentItemXYZ123") == []
