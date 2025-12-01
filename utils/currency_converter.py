from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class CurrencyConverter:
    EXCHANGE_RATES = {
        "COP": {
            "USD": Decimal("0.00025"),
            "EUR": Decimal("0.00023"),
        },
        "USD": {
            "COP": Decimal("4000.0"),
            "EUR": Decimal("0.92"),
        },
        "EUR": {
            "COP": Decimal("4350.0"),
            "USD": Decimal("1.09"),
        },
    }

    @staticmethod
    def convert(amount, from_currency, to_currency):
        if from_currency == to_currency:
            return amount

        if from_currency not in CurrencyConverter.EXCHANGE_RATES:
            raise ValueError(f"Moneda origen no soportada: {from_currency}")

        if to_currency not in CurrencyConverter.EXCHANGE_RATES[from_currency]:
            raise ValueError(f"Conversión no soportada: {from_currency} -> {to_currency}")

        rate = CurrencyConverter.EXCHANGE_RATES[from_currency][to_currency]

        amount_decimal = Decimal(str(amount)) / Decimal("100")
        converted = amount_decimal * rate

        return int(round(converted * 100))

    @staticmethod
    def get_exchange_rate(from_currency, to_currency):
        if from_currency == to_currency:
            return Decimal("1.00")

        if from_currency not in CurrencyConverter.EXCHANGE_RATES:
            raise ValueError(f"Moneda origen no soportada: {from_currency}")

        if to_currency not in CurrencyConverter.EXCHANGE_RATES[from_currency]:
            raise ValueError(f"Conversión no soportada: {from_currency} -> {to_currency}")

        return CurrencyConverter.EXCHANGE_RATES[from_currency][to_currency]

    @staticmethod
    def get_supported_currencies():
        return list(CurrencyConverter.EXCHANGE_RATES.keys())

    @staticmethod
    def is_conversion_needed(account_currency, transaction_currency):
        return account_currency != transaction_currency
