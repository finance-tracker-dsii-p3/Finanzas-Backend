from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .currency_converter import CurrencyConverter
import logging

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_exchange_rate(request):
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
