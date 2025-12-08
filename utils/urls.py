"""
URLs para utilidades del sistema
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para viewsets
router = DefaultRouter()
router.register(r'base-currency', views.BaseCurrencyViewSet, basename='base-currency')
router.register(r'exchange-rates', views.ExchangeRateViewSet, basename='exchange-rates')

urlpatterns = [
    # Endpoints heredados (compatibilidad con código existente)
    path("currency/exchange-rate/", views.get_exchange_rate, name="exchange-rate"),
    path("currency/convert/", views.convert_currency, name="convert-currency"),
    
    # Nuevos endpoints para moneda base y tipos de cambio mensuales
    path("", include(router.urls)),
]

