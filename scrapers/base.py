from abc import ABC, abstractmethod
import logging
from typing import Any

from models.product import Product

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract Base Class for product scrapers implementing the Template Method Pattern.

    The Template Method Pattern defines the skeleton of the scraping algorithm in the
    `scrape()` method, deferring the platform-specific fetching and parsing steps to
    concrete subclasses while providing a standardized validation and error-handling pipeline.

    Subclasses must implement:
        - `platform_name`: Property returning the name of the marketplace.
        - `base_url`: Property returning the root URL for the platform.
        - `fetch(keyword)`: Retrieves raw data payload for the keyword.
        - `parse(raw_data)`: Maps platform-specific raw dictionaries into `Product` models.

    Subclasses may optionally override:
        - `validate(products)`: Custom validation hook for business logic.
    """

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Return the friendly name of the e-commerce platform."""
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        """Return the base URL of the e-commerce platform."""
        pass

    @abstractmethod
    def fetch(self, keyword: str) -> list[dict[str, Any]]:
        """Fetch raw data payload from the marketplace.

        Args:
            keyword: The search query string.

        Returns:
            A list of raw dictionary records retrieved from the platform.
        """
        pass

    @abstractmethod
    def parse(self, raw_data: list[dict[str, Any]]) -> list[Product]:
        """Parse raw marketplace response into domain Product objects.

        Args:
            raw_data: Raw dictionaries returned by `fetch()`.

        Returns:
            A list of `Product` instances mapped from the raw data.
        """
        pass

    def validate(self, products: list[Product]) -> list[Product]:
        """Validate and filter parsed products.

        Default validation ensures:
            1. Object is a valid `Product` instance.
            2. Price is strictly positive (> 0).
            3. Product name is not empty.
            4. Valid product URL is present.

        Can be overridden or augmented by subclasses.

        Args:
            products: Parsed `Product` instances to validate.

        Returns:
            A list of valid `Product` objects meeting all quality criteria.
        """
        validated_products: list[Product] = []
        for product in products:
            if not isinstance(product, Product):
                logger.warning(f"[{self.platform_name}] Skipped non-Product object: {product}")
                continue

            if product.price <= 0:
                logger.warning(
                    f"[{self.platform_name}] Skipped item with non-positive price: {product.name} ({product.price})"
                )
                continue

            if not product.name.strip():
                logger.warning(f"[{self.platform_name}] Skipped item with empty name.")
                continue

            if not product.url.strip():
                logger.warning(f"[{self.platform_name}] Skipped item without URL: {product.name}")
                continue

            validated_products.append(product)

        return validated_products

    def scrape(self, keyword: str) -> list[Product]:
        """Template Method defining the standardized scraping lifecycle.

        Lifecycle Steps:
            1. Fetch raw data: `fetch(keyword)`
            2. Parse raw data into domain entities: `parse(raw_data)`
            3. Validate domain entities: `validate(products)`

        Args:
            keyword: Search query string.

        Returns:
            A list of validated `Product` domain models.
        """
        logger.info(f"[{self.platform_name}] Starting scraping lifecycle for '{keyword}'...")

        # Step 1: Fetch
        raw_data = self.fetch(keyword)
        logger.debug(f"[{self.platform_name}] Fetched {len(raw_data)} raw records.")

        # Step 2: Parse
        parsed_products = self.parse(raw_data)
        logger.debug(f"[{self.platform_name}] Parsed {len(parsed_products)} products.")

        # Step 3: Validate
        validated_products = self.validate(parsed_products)
        logger.info(
            f"[{self.platform_name}] Successfully scraped and validated {len(validated_products)} products."
        )

        return validated_products
