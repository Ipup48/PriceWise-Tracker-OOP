"""Main entry point and demonstration for Price Comparison Tracker.

Demonstrates:
    - Object-Oriented Analysis & Design (OOAD)
    - Template Method Pattern in scrapers
    - Composition & Dependency Injection in PriceComparisonEngine
    - Separation of Concerns with Currency Normalization
    - Open/Closed Principle (dynamically adding a new scraper at runtime)
"""

import sys
from typing import Any

# Ensure terminal stdout handles Unicode cleanly across platforms
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from engine.comparison import ComparisonResult, PriceComparisonEngine
from engine.currency import FixedRateCurrencyConverter
from models.product import Product
from scrapers.base import BaseScraper
from scrapers.lazada import MockLazadaScraper
from scrapers.shopee import MockShopeeScraper


def print_comparison_table(result: ComparisonResult) -> None:
    """Render a clean, formatted ASCII table of comparison results."""
    print(f"\n{'=' * 95}")
    print(f" SEARCH RESULTS FOR: '{result.keyword}' (Normalized to: {result.target_currency})")
    print(f"{'=' * 95}")

    if not result.items:
        print(f"  [!] No products found matching '{result.keyword}'.")
        print(f"{'=' * 95}\n")
        return

    # Table Header
    header = (
        f"{'Rank':<5} | {'Platform':<8} | {'Product Name':<38} | "
        f"{'Orig Price':<12} | {'Norm Price':<12} | {'Stock':<6}"
    )
    print(header)
    print(f"{'-' * 5}-+-{'-' * 8}-+-{'-' * 38}-+-{'-' * 12}-+-{'-' * 12}-+-{'-' * 6}")

    for idx, item in enumerate(result.items, start=1):
        prod = item.product
        stock_str = "YES" if prod.in_stock else "NO"
        # Truncate long names for clean table formatting
        display_name = prod.name if len(prod.name) <= 38 else prod.name[:35] + "..."
        orig_price = prod.formatted_price()
        norm_price = item.formatted_normalized_price()

        row = (
            f"#{idx:<4} | {prod.platform:<8} | {display_name:<38} | "
            f"{orig_price:<12} | {norm_price:<12} | {stock_str:<6}"
        )
        print(row)

    print(f"{'=' * 95}")

    # Summary Statistics
    if result.best_deal:
        best_p = result.best_deal.product
        print(
            f"[*] BEST DEAL: {best_p.name} on [{best_p.platform}] "
            f"at {result.best_deal.formatted_normalized_price()} "
            f"({'In Stock' if best_p.in_stock else 'Out of Stock'})"
        )
    print(
        f"[*] SUMMARY  : Total Found: {result.total_count} | "
        f"In Stock: {len(result.in_stock_items)} | "
        f"Min: {result.target_currency} {result.min_price:,.2f} | "
        f"Max: {result.target_currency} {result.max_price:,.2f} | "
        f"Avg: {result.target_currency} {result.average_price:,.2f}"
    )
    if result.errors:
        print(f"[!] Platform Errors: {result.errors}")
    print(f"{'=' * 95}\n")


# ----------------------------------------------------------------------
# Demonstration of Open/Closed Principle:
# Adding a new scraper without modifying existing scraper or engine code!
# ----------------------------------------------------------------------
class MockAmazonScraper(BaseScraper):
    """Dynamic extension scraper demonstrating the Open/Closed Principle (OCP)."""

    def __init__(self) -> None:
        self._platform_name = "Amazon"
        self._base_url = "https://www.amazon.com"
        self._catalog = [
            {
                "asin": "B09XS7JWHH",
                "title": "Sony WH-1000XM5 Wireless Industry Leading Noise Canceling (Silver)",
                "price_usd": 328.00,  # ~11,972 THB
                "is_prime_in_stock": True,
            },
            {
                "asin": "B0BDHWDR12",
                "title": "Apple AirPods Pro (2nd Gen)",
                "price_usd": 199.00,  # ~7,263.50 THB - Beats both Shopee and Lazada!
                "is_prime_in_stock": True,
            },
        ]

    @property
    def platform_name(self) -> str:
        return self._platform_name

    @property
    def base_url(self) -> str:
        return self._base_url

    def fetch(self, keyword: str) -> list[dict[str, Any]]:
        tokens = keyword.lower().split()
        return [
            item
            for item in self._catalog
            if any(token in item["title"].lower() for token in tokens)
        ]

    def parse(self, raw_data: list[dict[str, Any]]) -> list[Product]:
        return [
            Product(
                name=raw["title"],
                price=float(raw["price_usd"]),
                currency="USD",
                platform=self.platform_name,
                url=f"{self.base_url}/dp/{raw['asin']}",
                in_stock=raw["is_prime_in_stock"],
            )
            for raw in raw_data
        ]


def main() -> None:
    """Run the demonstration scenarios showcasing OOP and OOAD design."""
    print("=" * 95)
    print(" PRICE COMPARISON TRACKER (OOAD & OOP ARCHITECTURE DEMONSTRATION)")
    print("=" * 95)

    # 1. Dependency Injection: Initialize Currency Converter & Scrapers
    currency_converter = FixedRateCurrencyConverter(
        {
            "USD": 1.0,
            "THB": 36.50,
            "EUR": 0.92,
        }
    )

    shopee_scraper = MockShopeeScraper()
    lazada_scraper = MockLazadaScraper()

    # 2. Composition: Engine receives dependencies
    engine = PriceComparisonEngine(
        scrapers=[shopee_scraper, lazada_scraper],
        currency_converter=currency_converter,
        target_currency="THB",
    )

    print(f"\n[+] Registered Scrapers: {[s.platform_name for s in engine.get_registered_scrapers()]}")
    print("[+] Base Comparison Currency: THB (Exchange Rate: 1 USD = 36.50 THB)")

    # Scenario 1: Same Currency Price Comparison (Sony Headphones)
    print("\n--- SCENARIO 1: Direct Price Comparison (Sony WH-1000XM5) ---")
    result_sony = engine.compare("Sony")
    print_comparison_table(result_sony)

    # Scenario 2: Cross-Border Currency Conversion (AirPods Pro - THB vs USD)
    print("\n--- SCENARIO 2: Cross-Border Currency Normalization (Apple AirPods) ---")
    result_airpods = engine.compare("AirPods")
    print_comparison_table(result_airpods)

    # Scenario 3: Stock Filtering (Logitech MX Master 3S)
    print("\n--- SCENARIO 3: Stock Status & Filtering (Logitech Mouse) ---")
    print(">>> (A) All Items (including Out of Stock):")
    result_mouse_all = engine.compare("Logitech", in_stock_only=False)
    print_comparison_table(result_mouse_all)

    print(">>> (B) In-Stock Only Items:")
    result_mouse_instock = engine.compare("Logitech", in_stock_only=True)
    print_comparison_table(result_mouse_instock)

    # Scenario 4: Demonstrating Open/Closed Principle (Extending with Amazon)
    print("\n--- SCENARIO 4: Open/Closed Principle (Adding Amazon Scraper Dynamically) ---")
    amazon_scraper = MockAmazonScraper()
    engine.register_scraper(amazon_scraper)
    print(f"[+] Dynamically registered new scraper: '{amazon_scraper.platform_name}'")
    print(f"[+] Total Active Scrapers: {[s.platform_name for s in engine.get_registered_scrapers()]}")

    print(">>> Re-comparing 'AirPods' with Amazon included:")
    result_expanded = engine.compare("AirPods")
    print_comparison_table(result_expanded)


if __name__ == "__main__":
    # If user passes search keyword from CLI: python main.py <query>
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        eng = PriceComparisonEngine(
            scrapers=[MockShopeeScraper(), MockLazadaScraper()],
            currency_converter=FixedRateCurrencyConverter(),
            target_currency="THB",
        )
        res = eng.compare(query)
        print_comparison_table(res)
    else:
        main()
