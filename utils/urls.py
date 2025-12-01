"""
URLs para utilidades del sistema
"""

from django.urls import path
from . import views

urlpatterns = [
    path("currency/exchange-rate/", views.get_exchange_rate, name="exchange-rate"),
    path("currency/convert/", views.convert_currency, name="convert-currency"),
]
