from decimal import Decimal
from datetime import date
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)


class CurrencyConverter:
    """
    Clase heredada para mantener compatibilidad con código existente.
    Usa tasas estáticas para conversiones rápidas cuando no se requiere histórico.
    """
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
        """
        Conversión simple con tasas estáticas (para compatibilidad).
        Para conversiones con histórico mensual, usar FxService.
        """
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


class FxService:
    """
    Servicio de conversión de monedas con soporte para moneda base por usuario
    y tipos de cambio mensuales históricos.
    
    Características:
    - Moneda base configurable por usuario
    - Tipos de cambio mensuales con histórico
    - Fallback a último tipo de cambio disponible
    - Advertencias cuando falta configuración
    """
    DEFAULT_BASE = "COP"
    SUPPORTED_CURRENCIES = ["COP", "USD", "EUR"]

    @staticmethod
    def get_base_currency(user):
        """
        Obtiene la moneda base configurada para un usuario.
        Si no tiene configuración, retorna COP por defecto.
        
        Args:
            user: Usuario autenticado o None
            
        Returns:
            str: Código de moneda base (COP, USD, EUR)
        """
        if not user or user.is_anonymous:
            return FxService.DEFAULT_BASE
        
        # Import local para evitar circular dependency
        from utils.models import BaseCurrencySetting
        
        setting = BaseCurrencySetting.objects.filter(user=user).first()
        return setting.base_currency if setting else FxService.DEFAULT_BASE

    @staticmethod
    def set_base_currency(user, base_currency):
        """
        Define la moneda base para un usuario.
        
        Args:
            user: Usuario autenticado
            base_currency: Código de moneda (COP, USD, EUR)
            
        Returns:
            str: Moneda base configurada
            
        Raises:
            ValueError: Si la moneda no está soportada
        """
        FxService.ensure_supported(base_currency)
        
        from utils.models import BaseCurrencySetting
        
        BaseCurrencySetting.objects.update_or_create(
            user=user, 
            defaults={"base_currency": base_currency}
        )
        return base_currency

    @staticmethod
    def _get_rate_record(currency, base_currency, ref_date: date):
        """
        Busca el tipo de cambio para una fecha específica.
        Si no existe para el mes exacto, usa el último disponible anterior.
        
        Args:
            currency: Moneda origen
            base_currency: Moneda destino
            ref_date: Fecha de referencia
            
        Returns:
            tuple: (rate, warning_message) - tasa y mensaje de advertencia si aplica
            
        Raises:
            ValueError: Si no hay ningún tipo de cambio disponible
        """
        if currency == base_currency:
            return Decimal("1"), None
        
        from utils.models import ExchangeRate
        
        year = ref_date.year
        month = ref_date.month
        
        # Buscar tipo de cambio exacto o anterior
        record = (
            ExchangeRate.objects.filter(
                Q(year__lt=year) | Q(year=year, month__lte=month),
                currency=currency,
                base_currency=base_currency,
            )
            .order_by("-year", "-month")
            .first()
        )
        
        warning = None
        if record:
            # Si no es del mes exacto, generar advertencia
            if record.year != year or record.month != month:
                warning = (
                    f"No hay tipo de cambio para {currency}->{base_currency} "
                    f"en {year}-{month:02d}. Usando tasa de "
                    f"{record.year}-{record.month:02d}: {record.rate}"
                )
            return record.rate, warning
        
        # Intentar búsqueda inversa
        inv = (
            ExchangeRate.objects.filter(
                Q(year__lt=year) | Q(year=year, month__lte=month),
                currency=base_currency,
                base_currency=currency,
            )
            .order_by("-year", "-month")
            .first()
        )
        
        if inv:
            if inv.year != year or inv.month != month:
                warning = (
                    f"No hay tipo de cambio para {currency}->{base_currency} "
                    f"en {year}-{month:02d}. Usando tasa inversa de "
                    f"{inv.year}-{inv.month:02d}"
                )
            return Decimal("1") / inv.rate, warning
        
        # Si no hay ninguna tasa, usar tasa estática como fallback y advertir
        try:
            static_rate = CurrencyConverter.get_exchange_rate(currency, base_currency)
            warning = (
                f"⚠️ No hay tipo de cambio histórico para {currency}->{base_currency}. "
                f"Usando tasa estática: {static_rate}"
            )
            return static_rate, warning
        except ValueError:
            raise ValueError(
                f"No hay tipo de cambio para {currency}->{base_currency} "
                f"en {year}-{month:02d} ni en períodos anteriores"
            )

    @staticmethod
    def convert_amount(amount_cents: int, from_currency: str, to_currency: str, ref_date: date):
        """
        Convierte un monto de una moneda a otra usando el tipo de cambio del período.
        
        Args:
            amount_cents: Monto en centavos (ej: 10000 = 100.00)
            from_currency: Moneda origen (COP, USD, EUR)
            to_currency: Moneda destino
            ref_date: Fecha de referencia para el tipo de cambio
            
        Returns:
            tuple: (converted_cents, rate, warning) - monto convertido, tasa usada, advertencia si aplica
        """
        if from_currency == to_currency:
            return amount_cents, Decimal("1"), None
        
        rate, warning = FxService._get_rate_record(from_currency, to_currency, ref_date)
        # Convertir de centavos a unidades decimales
        amount_decimal = Decimal(str(amount_cents)) / Decimal("100")
        # Multiplicar por la tasa
        converted_decimal = amount_decimal * rate
        # Convertir de vuelta a centavos, redondeando apropiadamente
        converted_cents = int((converted_decimal * Decimal("100")).quantize(Decimal("1")))
        
        return converted_cents, rate, warning

    @staticmethod
    def convert_to_base(amount_cents: int, txn_currency: str, base_currency: str, ref_date: date):
        """
        Convierte un monto a la moneda base del usuario.
        Método de conveniencia para conversiones a moneda base.
        
        Args:
            amount_cents: Monto en centavos
            txn_currency: Moneda de la transacción
            base_currency: Moneda base del usuario
            ref_date: Fecha de la transacción
            
        Returns:
            tuple: (converted_cents, rate, warning)
        """
        return FxService.convert_amount(amount_cents, txn_currency, base_currency, ref_date)

    @staticmethod
    def ensure_supported(currency: str):
        """
        Valida que una moneda esté soportada por el sistema.
        
        Args:
            currency: Código de moneda
            
        Returns:
            bool: True si está soportada
            
        Raises:
            ValueError: Si la moneda no está soportada
        """
        if currency not in FxService.SUPPORTED_CURRENCIES:
            raise ValueError(
                f"Moneda no soportada: {currency}. "
                f"Monedas válidas: {', '.join(FxService.SUPPORTED_CURRENCIES)}"
            )
        return True
