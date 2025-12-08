"""
Vistas para configuración de monedas y tipos de cambio
"""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime, date
from decimal import Decimal
from django.utils import timezone

from utils.models import BaseCurrencySetting, ExchangeRate
from utils.serializers import BaseCurrencySerializer, ExchangeRateSerializer
from utils.currency_converter import CurrencyConverter, FxService
import logging

logger = logging.getLogger(__name__)


# ========== Endpoints heredados (para compatibilidad) ==========

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_exchange_rate(request):
    """Endpoint heredado - usa tasas estáticas de CurrencyConverter"""
    from_currency = request.query_params.get("from", "").upper()
    to_currency = request.query_params.get("to", "").upper()

    if not from_currency or not to_currency:
        return Response(
            {"error": 'Los parámetros "from" y "to" son requeridos'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        rate = CurrencyConverter.get_exchange_rate(from_currency, to_currency)

        return Response(
            {
                "from": from_currency,
                "to": to_currency,
                "rate": float(rate),
                "last_updated": timezone.now().isoformat(),
            }
        )
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def convert_currency(request):
    """Endpoint heredado - usa tasas estáticas de CurrencyConverter"""
    try:
        amount = int(request.query_params.get("amount", 0))
        from_currency = request.query_params.get("from", "").upper()
        to_currency = request.query_params.get("to", "").upper()

        if amount <= 0:
            return Response(
                {"error": "El monto debe ser mayor que cero"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not from_currency or not to_currency:
            return Response(
                {"error": 'Los parámetros "from" y "to" son requeridos'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        converted_amount = CurrencyConverter.convert(amount, from_currency, to_currency)
        rate = CurrencyConverter.get_exchange_rate(from_currency, to_currency)

        return Response(
            {
                "original_amount": amount,
                "original_currency": from_currency,
                "converted_amount": converted_amount,
                "converted_currency": to_currency,
                "exchange_rate": float(rate),
            }
        )
    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error en conversión de moneda: {str(e)}")
        return Response(
            {"error": "Error al convertir moneda"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ========== ViewSets para gestión de moneda base y tipos de cambio ==========

class BaseCurrencyViewSet(viewsets.ViewSet):
    """
    ViewSet para gestionar la moneda base del usuario.
    
    - GET /api/utils/base-currency/: Consultar moneda base actual
    - PUT /api/utils/base-currency/: Definir/actualizar moneda base (sin ID en URL)
    """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """Obtiene la moneda base actual del usuario"""
        base_currency = FxService.get_base_currency(request.user)
        setting = BaseCurrencySetting.objects.filter(user=request.user).first()
        
        return Response({
            "base_currency": base_currency,
            "updated_at": setting.updated_at if setting else None,
            "available_currencies": FxService.SUPPORTED_CURRENCIES
        })

    @action(detail=False, methods=['put'])
    def set_base(self, request):
        """Define o actualiza la moneda base del usuario"""
        serializer = BaseCurrencySerializer(
            data=request.data,
            context={"request": request}
        )
        
        if serializer.is_valid():
            instance = serializer.save()
            return Response({
                "base_currency": instance.base_currency,
                "updated_at": instance.updated_at,
                "message": f"Moneda base actualizada a {instance.base_currency}. "
                          "Los totales se recalcularán automáticamente."
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExchangeRateViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar tipos de cambio mensuales.
    
    - GET: Listar tipos de cambio
    - POST: Crear nuevo tipo de cambio
    - PUT/PATCH: Actualizar tipo de cambio existente
    - DELETE: Eliminar tipo de cambio
    
    Acciones adicionales:
    - current: Obtener tipo de cambio vigente para una fecha
    - convert: Convertir un monto entre monedas
    """
    queryset = ExchangeRate.objects.all()
    serializer_class = ExchangeRateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filtra tipos de cambio por parámetros de query.
        Soporta: currency, base_currency, year, month
        """
        queryset = ExchangeRate.objects.all().order_by("-year", "-month", "currency")
        
        currency = self.request.query_params.get("currency")
        base_currency = self.request.query_params.get("base_currency")
        year = self.request.query_params.get("year")
        month = self.request.query_params.get("month")
        
        if currency:
            queryset = queryset.filter(currency=currency.upper())
        if base_currency:
            queryset = queryset.filter(base_currency=base_currency.upper())
        if year:
            queryset = queryset.filter(year=int(year))
        if month:
            queryset = queryset.filter(month=int(month))
        
        return queryset

    @action(detail=False, methods=["get"])
    def current(self, request):
        """
        Obtiene el tipo de cambio vigente para una moneda en una fecha específica.
        
        Query params:
        - currency: Moneda a consultar (requerido)
        - base: Moneda base (opcional, usa la del usuario si no se especifica)
        - date: Fecha de referencia en formato YYYY-MM-DD (opcional, usa hoy si no se especifica)
        
        Ejemplo:
        GET /api/utils/exchange-rates/current/?currency=USD&base=COP&date=2025-01-15
        """
        currency = request.query_params.get("currency")
        base = request.query_params.get("base")
        date_str = request.query_params.get("date")
        
        if not currency:
            return Response(
                {"error": "El parámetro 'currency' es requerido"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        currency = currency.upper()
        base_currency = base.upper() if base else FxService.get_base_currency(request.user)
        
        try:
            ref_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
        except ValueError:
            return Response(
                {"error": "Formato de fecha inválido. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Usar convert_amount con monto 100 para obtener la tasa
            _, rate, warning = FxService.convert_amount(100, currency, base_currency, ref_date)
            
            response_data = {
                "currency": currency,
                "base_currency": base_currency,
                "rate": float(rate),
                "reference_date": ref_date.isoformat(),
                "year": ref_date.year,
                "month": ref_date.month,
            }
            
            if warning:
                response_data["warning"] = warning
            
            return Response(response_data)
            
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["get"])
    def convert(self, request):
        """
        Convierte un monto entre dos monedas para una fecha específica.
        
        Query params:
        - amount: Monto a convertir en centavos (requerido)
        - from: Moneda origen (requerido)
        - to: Moneda destino (opcional, usa moneda base del usuario si no se especifica)
        - date: Fecha de referencia en formato YYYY-MM-DD (opcional, usa hoy si no se especifica)
        
        Ejemplo:
        GET /api/utils/exchange-rates/convert/?amount=10000&from=USD&to=COP&date=2025-01-15
        """
        amount_str = request.query_params.get("amount")
        from_currency = request.query_params.get("from")
        to_currency = request.query_params.get("to")
        date_str = request.query_params.get("date")
        
        if not amount_str or not from_currency:
            return Response(
                {"error": "Los parámetros 'amount' y 'from' son requeridos"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            amount = int(amount_str)
        except ValueError:
            return Response(
                {"error": "El monto debe ser un número entero en centavos"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from_currency = from_currency.upper()
        to_currency = to_currency.upper() if to_currency else FxService.get_base_currency(request.user)
        
        try:
            ref_date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else date.today()
        except ValueError:
            return Response(
                {"error": "Formato de fecha inválido. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            converted, rate, warning = FxService.convert_amount(
                amount, from_currency, to_currency, ref_date
            )
            
            # Determinar decimales según la moneda (COP no usa decimales en la práctica)
            from_decimals = 0 if from_currency == "COP" else 2
            to_decimals = 0 if to_currency == "COP" else 2
            
            response_data = {
                "original_amount": amount,
                "original_currency": from_currency,
                "converted_amount": converted,
                "target_currency": to_currency,
                "exchange_rate": float(rate),
                "reference_date": ref_date.isoformat(),
                "formatted": {
                    "original": f"{amount / 100:,.{from_decimals}f} {from_currency}",
                    "converted": f"{converted / 100:,.{to_decimals}f} {to_currency}",
                }
            }
            
            if warning:
                response_data["warning"] = warning
            
            return Response(response_data)
            
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

