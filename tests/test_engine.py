from typing import Any
import pytest

from engine.comparison import PriceComparisonEngine
from engine.currency import FixedRateCurrencyConverter
from models.product import Product
from scrapers.base import BaseScraper
from scrapers.lazada import MockLazadaScraper
from scrapers.shopee import MockShopeeScraper


class BrokenScraper(BaseScraper):
    """Failing scraper to test error isolation in the comparison engine."""

    @property
    def platform_name(self) -> str:
        return "BrokenPlatform"

    @property
    def base_url(self) -> str:
        return "https://broken.example.com"

    def fetch(self, keyword: str) -> list[dict[str, Any]]:
        raise ConnectionError("Simulated network timeout connecting to BrokenPlatform")

    def parse(self, raw_data: list[dict[str, Any]]) -> list[Product]:
        return []


def test_currency_converter_logic() -> None:
    """Test exchange rate conversions and custom rate updates."""
    converter = FixedRateCurrencyConverter({"EUR": 0.90, "THB": 36.00})

    # Test same currency
    assert converter.convert(100.0, "USD", "USD") == 100.0

    # 100 USD to THB = 3600.0 THB
    assert converter.convert(100.0, "USD", "THB") == 3600.0

    # Convert THB to USD: 3600 / 36 = 100.0
    assert converter.convert(3600.0, "THB", "USD") == 100.0

    # Dynamic rate update
    converter.set_rate("THB", 40.0)
    assert converter.convert(100.0, "USD", "THB") == 4000.0

    with pytest.raises(ValueError):
        converter.convert(10.0, "XYZ", "THB")


def test_engine_composition_and_dependency_injection() -> None:
    """Test engine accepts scrapers via constructor and registration methods."""
    shopee = MockShopeeScraper()
    lazada = MockLazadaScraper()

    # Constructor injection
    engine = PriceComparisonEngine(scrapers=[shopee])
    assert len(engine.get_registered_scrapers()) == 1

    # Registration method
    engine.register_scraper(lazada)
    assert len(engine.get_registered_scrapers()) == 2

    # Unregister
    removed = engine.unregister_scraper("Shopee")
    assert removed is True
    assert len(engine.get_registered_scrapers()) == 1

    # Invalid registration
    with pytest.raises(TypeError):
        engine.register_scraper("not a scraper")  # type: ignore[arg-type]


def test_engine_sorts_lowest_to_highest_price() -> None:
    """Verify products are sorted lowest-to-highest across multiple platforms."""
    shopee = MockShopeeScraper()
    lazada = MockLazadaScraper()
    engine = PriceComparisonEngine(scrapers=[shopee, lazada], target_currency="THB")

    # Search for Sony Headphones
    result = engine.compare("Sony")
    assert result.total_count == 2
    assert len(result.items) == 2

    # Check ascending order
    # Lazada is 11,450.00 THB vs Shopee 11,990.00 THB
    first_item = result.items[0]
    second_item = result.items[1]

    assert first_item.normalized_price <= second_item.normalized_price
    assert first_item.product.platform == "Lazada"
    assert first_item.normalized_price == 11450.00
    assert second_item.product.platform == "Shopee"
    assert second_item.normalized_price == 11990.00

    # Summary statistics
    assert result.best_deal is not None
    assert result.best_deal.product.platform == "Lazada"
    assert result.min_price == 11450.00
    assert result.max_price == 11990.00
    assert result.average_price == 11720.00


def test_engine_normalizes_cross_border_currencies() -> None:
    """Test comparison properly converts international currencies to target currency."""
    shopee = MockShopeeScraper()
    lazada = MockLazadaScraper()
    # 1 USD = 36.50 THB
    converter = FixedRateCurrencyConverter({"THB": 36.50, "USD": 1.00})
    engine = PriceComparisonEngine(
        scrapers=[shopee, lazada],
        currency_converter=converter,
        target_currency="THB",
    )

    # Search for AirPods
    # Shopee price: 7,890.00 THB
    # Lazada price: 219.00 USD -> 219 * 36.50 = 7,993.50 THB
    result = engine.compare("AirPods")
    assert result.total_count == 2

    cheapest = result.items[0]
    pricier = result.items[1]

    assert cheapest.product.platform == "Shopee"
    assert cheapest.normalized_price == 7890.00
    assert cheapest.product.currency == "THB"

    assert pricier.product.platform == "Lazada"
    assert pricier.normalized_price == 7993.50
    assert pricier.product.currency == "USD"
    assert result.best_deal == cheapest


def test_engine_in_stock_filter() -> None:
    """Test filtering by stock availability."""
    shopee = MockShopeeScraper()
    lazada = MockLazadaScraper()
    engine = PriceComparisonEngine(scrapers=[shopee, lazada])

    # Logitech is Out of Stock on Shopee, In Stock on Lazada
    unfiltered = engine.compare("Logitech", in_stock_only=False)
    assert unfiltered.total_count == 2

    filtered = engine.compare("Logitech", in_stock_only=True)
    assert filtered.total_count == 1
    assert filtered.items[0].product.platform == "Lazada"
    assert filtered.items[0].product.in_stock is True


def test_engine_fault_isolation() -> None:
    """Ensure that a failing scraper doesn't crash the engine for other scrapers."""
    shopee = MockShopeeScraper()
    broken = BrokenScraper()

    engine = PriceComparisonEngine(scrapers=[shopee, broken])
    result = engine.compare("Sony")

    # Shopee results should still succeed
    assert result.total_count >= 1
    assert result.items[0].product.platform == "Shopee"

    # Broken platform error is recorded
    assert "BrokenPlatform" in result.errors
    assert "Simulated network timeout" in result.errors["BrokenPlatform"]


def test_engine_empty_input_validation() -> None:
    """Test engine validates non-empty query string."""
    engine = PriceComparisonEngine()
    with pytest.raises(ValueError, match="Search keyword cannot be empty"):
        engine.compare("   ")
