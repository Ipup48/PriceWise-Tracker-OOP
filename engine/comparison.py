from dataclasses import dataclass, field
import logging
from typing import Sequence

from engine.currency import FixedRateCurrencyConverter, ICurrencyConverter
from models.product import Product
from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ComparisonItem:
    """Represents a product item paired with its normalized comparison price.

    Attributes:
        product: The original scraped domain `Product`.
        normalized_price: The price converted into the engine's target comparison currency.
        target_currency: ISO currency code of the normalized price.
    """

    product: Product
    normalized_price: float
    target_currency: str

    def formatted_normalized_price(self) -> str:
        """Return formatted price in the target comparison currency."""
        return f"{self.target_currency.upper()} {self.normalized_price:,.2f}"


@dataclass
class ComparisonResult:
    """Aggregated comparison report across all scraped marketplace platforms.

    Attributes:
        keyword: The query string searched across platforms.
        target_currency: The currency used for price comparison normalization.
        items: List of `ComparisonItem` instances sorted lowest-to-highest price.
        errors: Dictionary mapping platform names to error messages if any failed.
    """

    keyword: str
    target_currency: str
    items: list[ComparisonItem] = field(default_factory=list)
    errors: dict[str, str] = field(default_factory=dict)

    @property
    def total_count(self) -> int:
        """Total number of products found."""
        return len(self.items)

    @property
    def in_stock_items(self) -> list[ComparisonItem]:
        """List of items currently in stock."""
        return [item for item in self.items if item.product.in_stock]

    @property
    def best_deal(self) -> ComparisonItem | None:
        """The lowest priced in-stock product, or lowest overall if none in stock."""
        in_stock = self.in_stock_items
        if in_stock:
            return in_stock[0]
        return self.items[0] if self.items else None

    @property
    def min_price(self) -> float:
        """Minimum normalized price in the result set (0.0 if empty)."""
        return self.items[0].normalized_price if self.items else 0.0

    @property
    def max_price(self) -> float:
        """Maximum normalized price in the result set (0.0 if empty)."""
        return self.items[-1].normalized_price if self.items else 0.0

    @property
    def average_price(self) -> float:
        """Average normalized price across all found products."""
        if not self.items:
            return 0.0
        return round(sum(item.normalized_price for item in self.items) / len(self.items), 2)


class PriceComparisonEngine:
    """Coordinates multiple marketplace scrapers, normalizes prices, and ranks deals.

    Follows:
        - Composition: Holds a collection of `BaseScraper` instances.
        - Dependency Injection: Accepts scrapers and currency converter via constructor
          or registration methods.
        - Open/Closed Principle: Open to new scrapers without altering comparison logic.
        - Single Responsibility Principle: Solely responsible for orchestrating
          queries, aggregating data, normalizing currency, and sorting results.
    """

    def __init__(
        self,
        scrapers: Sequence[BaseScraper] | None = None,
        currency_converter: ICurrencyConverter | None = None,
        target_currency: str = "THB",
    ) -> None:
        """Initialize the price comparison engine.

        Args:
            scrapers: Optional initial list of marketplace scrapers to register.
            currency_converter: Service implementing `ICurrencyConverter`.
                                Defaults to `FixedRateCurrencyConverter` if None.
            target_currency: Currency to normalize and sort prices against (default 'THB').
        """
        self._scrapers: dict[str, BaseScraper] = {}
        self._currency_converter: ICurrencyConverter = (
            currency_converter if currency_converter is not None else FixedRateCurrencyConverter()
        )
        self._target_currency: str = target_currency.upper()

        if scrapers:
            for scraper in scrapers:
                self.register_scraper(scraper)

    @property
    def target_currency(self) -> str:
        """The target currency code used for comparisons."""
        return self._target_currency

    @target_currency.setter
    def target_currency(self, currency: str) -> None:
        """Set the target currency code."""
        if not currency or len(currency.strip()) != 3:
            raise ValueError(f"Invalid currency code: {currency}")
        self._target_currency = currency.strip().upper()

    def register_scraper(self, scraper: BaseScraper) -> None:
        """Register a new scraper into the engine.

        Args:
            scraper: An instance implementing `BaseScraper`.
        """
        if not isinstance(scraper, BaseScraper):
            raise TypeError(f"Scraper must be an instance of BaseScraper, got {type(scraper)}")

        platform_key = scraper.platform_name.strip().lower()
        self._scrapers[platform_key] = scraper
        logger.info(f"Registered scraper for platform: '{scraper.platform_name}'")

    def unregister_scraper(self, platform_name: str) -> bool:
        """Remove a registered scraper by platform name.

        Args:
            platform_name: The name of the platform to remove.

        Returns:
            True if removed, False if not found.
        """
        platform_key = platform_name.strip().lower()
        if platform_key in self._scrapers:
            del self._scrapers[platform_key]
            logger.info(f"Unregistered scraper for platform: '{platform_name}'")
            return True
        return False

    def get_registered_scrapers(self) -> list[BaseScraper]:
        """Return list of all currently registered scrapers."""
        return list(self._scrapers.values())

    def compare(
        self,
        keyword: str,
        in_stock_only: bool = False,
    ) -> ComparisonResult:
        """Scrape all registered marketplaces, aggregate products, and sort lowest-to-highest.

        Args:
            keyword: Product search query.
            in_stock_only: If True, filters out items marked out of stock.

        Returns:
            A `ComparisonResult` object with sorted items and summary statistics.
        """
        if not keyword or not keyword.strip():
            raise ValueError("Search keyword cannot be empty.")

        clean_keyword = keyword.strip()
        all_comparison_items: list[ComparisonItem] = []
        errors: dict[str, str] = {}

        # 1. Aggregate from all registered scrapers with fault isolation
        for platform_key, scraper in self._scrapers.items():
            try:
                products = scraper.scrape(clean_keyword)
                for product in products:
                    if in_stock_only and not product.in_stock:
                        continue

                    # 2. Normalize price into target comparison currency
                    normalized = self._currency_converter.convert(
                        amount=product.price,
                        from_currency=product.currency,
                        to_currency=self._target_currency,
                    )

                    all_comparison_items.append(
                        ComparisonItem(
                            product=product,
                            normalized_price=normalized,
                            target_currency=self._target_currency,
                        )
                    )
            except Exception as exc:
                error_msg = f"Failed to scrape from {scraper.platform_name}: {exc}"
                logger.error(error_msg, exc_info=True)
                errors[scraper.platform_name] = str(exc)

        # 3. Sort items lowest-to-highest price
        all_comparison_items.sort(key=lambda item: item.normalized_price)

        return ComparisonResult(
            keyword=clean_keyword,
            target_currency=self._target_currency,
            items=all_comparison_items,
            errors=errors,
        )
