"""
URLs para utilidades del sistema
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para viewsets
router = DefaultRouter()

# /api/utils/base-currency/ - Gestión de moneda base del usuario
# GET   /api/utils/base-currency/           - Obtener moneda base actual
# POST  /api/utils/base-currency/          - Crear/actualizar moneda base
# GET   /api/utils/base-currency/{id}/     - Ver detalle de configuración
# PUT   /api/utils/base-currency/{id}/     - Actualizar moneda base
# PATCH /api/utils/base-currency/{id}/     - Actualizar moneda base parcial
router.register(r"base-currency", views.BaseCurrencyViewSet, basename="base-currency")

# /api/utils/exchange-rates/ - Gestión de tipos de cambio históricos mensuales
# GET   /api/utils/exchange-rates/         - Listar tipos de cambio (filtros: year, month, from_currency, to_currency)
# POST  /api/utils/exchange-rates/         - Crear tipo de cambio mensual
# GET   /api/utils/exchange-rates/{id}/    - Ver detalle de tipo de cambio
# PUT   /api/utils/exchange-rates/{id}/    - Actualizar tipo de cambio
# PATCH /api/utils/exchange-rates/{id}/    - Actualizar tipo de cambio parcial
# DELETE /api/utils/exchange-rates/{id}/   - Eliminar tipo de cambio
router.register(r"exchange-rates", views.ExchangeRateViewSet, basename="exchange-rates")

urlpatterns = [
    # Endpoints heredados (compatibilidad con código existente)
    # GET /api/utils/currency/exchange-rate/?from_currency=USD&to_currency=COP&date=2025-12-08
    path("currency/exchange-rate/", views.get_exchange_rate, name="exchange-rate"),
    # POST /api/utils/currency/convert/ {\"amount\": 100, \"from_currency\": \"USD\", \"to_currency\": \"COP\", \"date\": \"2025-12-08\"}
    path("currency/convert/", views.convert_currency, name="convert-currency"),
    # Nuevos endpoints para moneda base y tipos de cambio mensuales
    path("", include(router.urls)),
]
