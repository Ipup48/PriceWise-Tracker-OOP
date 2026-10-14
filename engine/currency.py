from abc import ABC, abstractmethod


class ICurrencyConverter(ABC):
    """Abstract interface for currency exchange rate conversion."""

    @abstractmethod
    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        """Convert an amount from one currency to another.

        Args:
            amount: The numerical amount to convert.
            from_currency: ISO 4217 code of source currency.
            to_currency: ISO 4217 code of target currency.

        Returns:
            Converted amount in target currency rounded to 2 decimal places.
        """
        pass

    @abstractmethod
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """Retrieve exchange rate between two currencies."""
        pass


class FixedRateCurrencyConverter(ICurrencyConverter):
    """Concrete currency converter using configurable fixed exchange rates.

    Rates are stored relative to USD as a standard pivot currency.
    Follows Open/Closed Principle: new currencies or rates can be registered
    at runtime without modifying converter logic.
    """

    def __init__(self, rates_to_usd: dict[str, float] | None = None) -> None:
        """Initialize converter with exchange rates against 1 USD.

        Args:
            rates_to_usd: Dictionary mapping uppercase currency codes to units per 1 USD.
        """
        # Default baseline exchange rates (1 USD = X Currency)
        self._rates_to_usd: dict[str, float] = {
            "USD": 1.0,
            "THB": 36.50,
            "EUR": 0.92,
            "GBP": 0.79,
            "JPY": 155.00,
            "SGD": 1.35,
        }
        if rates_to_usd:
            self._rates_to_usd.update({k.upper(): v for k, v in rates_to_usd.items()})

    def set_rate(self, currency: str, rate_to_usd: float) -> None:
        """Update or register an exchange rate for a currency against 1 USD."""
        if rate_to_usd <= 0:
            raise ValueError(f"Exchange rate must be positive: {rate_to_usd}")
        self._rates_to_usd[currency.upper()] = rate_to_usd

    def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """Get exchange rate multiplier from source to target currency."""
        from_code = from_currency.upper()
        to_code = to_currency.upper()

        if from_code == to_code:
            return 1.0

        if from_code not in self._rates_to_usd:
            raise ValueError(f"Unsupported source currency: {from_code}")
        if to_code not in self._rates_to_usd:
            raise ValueError(f"Unsupported target currency: {to_code}")

        # Conversion via USD pivot:
        # 1 from_currency = (1 / rates[from]) USD
        # USD to target = USD * rates[to]
        # rate = rates[to] / rates[from]
        rate = self._rates_to_usd[to_code] / self._rates_to_usd[from_code]
        return rate

    def convert(self, amount: float, from_currency: str, to_currency: str) -> float:
        """Convert amount between two currencies."""
        if amount == 0:
            return 0.0
        rate = self.get_exchange_rate(from_currency, to_currency)
        return round(amount * rate, 2)
