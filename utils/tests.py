"""
Tests para funcionalidad de multi-moneda (HU-17)
"""

from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from utils.currency_converter import FxService
from utils.models import ExchangeRate

User = get_user_model()


class BaseCurrencySettingTest(TestCase):
    """Tests para configuración de moneda base"""

    def setUp(self):
        self.user = User.objects.create_user(
            identification="FX-TEST-001",
            username="fxuser",
            email="fx@test.com",
            password="testpass123",
            role="user",
        )

    def test_default_base_currency(self):
        """Usuario sin configuración debe retornar COP por defecto"""
        base = FxService.get_base_currency(self.user)
        assert base == "COP"

    def test_set_base_currency(self):
        """Establecer moneda base del usuario"""
        FxService.set_base_currency(self.user, "USD")
        base = FxService.get_base_currency(self.user)
        assert base == "USD"

    def test_update_base_currency(self):
        """Actualizar moneda base existente"""
        FxService.set_base_currency(self.user, "COP")
        FxService.set_base_currency(self.user, "EUR")
        base = FxService.get_base_currency(self.user)
        assert base == "EUR"


class ExchangeRateTest(TestCase):
    """Tests para tipos de cambio"""

    def setUp(self):
        self.rate = ExchangeRate.objects.create(
            base_currency="COP",
            currency="USD",
            year=2025,
            month=1,
            rate=Decimal("3750.0"),
            source="test",
        )

    def test_create_exchange_rate(self):
        """Crear tipo de cambio"""
        assert self.rate.currency == "USD"
        assert self.rate.rate == Decimal("3750.0")
        assert str(self.rate) == "USD/COP 2025-01: 3750.0"

    def test_unique_constraint(self):
        """No permitir duplicados del mismo período"""
        with pytest.raises(Exception):
            ExchangeRate.objects.create(
                base_currency="COP",
                currency="USD",
                year=2025,
                month=1,
                rate=Decimal("3800.0"),
            )


class FxServiceTest(TestCase):
    """Tests para servicio de conversión"""

    def setUp(self):
        self.user = User.objects.create_user(
            identification="FX-TEST-002",
            username="fxuser2",
            email="fx2@test.com",
            password="testpass123",
            role="user",
        )
        ExchangeRate.objects.create(
            base_currency="COP",
            currency="USD",
            year=2025,
            month=1,
            rate=Decimal("4000.0"),
        )

    def test_convert_same_currency(self):
        """Convertir misma moneda retorna igual"""
        converted, rate, warning = FxService.convert_amount(10000, "COP", "COP", date(2025, 1, 15))
        assert converted == 10000
        assert rate == Decimal(1)
        assert warning is None

    def test_convert_cop_to_usd(self):
        """Convertir COP a USD usando tasa inversa"""
        converted, _rate, warning = FxService.convert_amount(
            400000000, "COP", "USD", date(2025, 1, 15)
        )
        # 4,000,000 COP / 4000 = 1,000 USD = 100,000 centavos
        assert converted == 100000
        assert warning is None

    def test_convert_usd_to_cop(self):
        """Convertir USD a COP"""
        converted, rate, warning = FxService.convert_amount(10000, "USD", "COP", date(2025, 1, 15))
        # 100 USD * 4000 = 400,000 COP = 40,000,000 centavos
        assert converted == 40000000
        assert rate == Decimal("4000.0")
        assert warning is None

    def test_fallback_to_previous_month(self):
        """Usar tipo de cambio de mes anterior si no existe el actual"""
        converted, _rate, warning = FxService.convert_amount(10000, "USD", "COP", date(2025, 2, 15))
        # Debe usar la tasa de enero 2025
        assert converted == 40000000
        assert warning is not None
        assert "2025-02" in warning


class BaseCurrencyAPITest(TestCase):
    """Tests para endpoints de moneda base"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            identification="API-TEST-001",
            username="apiuser",
            email="api@test.com",
            password="testpass123",
            role="user",
        )
        self.client.force_authenticate(user=self.user)

    def test_get_base_currency(self):
        """GET /api/utils/base-currency/"""
        response = self.client.get("/api/utils/base-currency/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["base_currency"] == "COP"

    def test_set_base_currency(self):
        """PUT /api/utils/base-currency/set_base/"""
        response = self.client.put(
            "/api/utils/base-currency/set_base/",
            {"base_currency": "USD"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["base_currency"] == "USD"

    def test_set_invalid_currency(self):
        """Rechazar moneda no soportada"""
        response = self.client.put(
            "/api/utils/base-currency/set_base/",
            {"base_currency": "GBP"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class ExchangeRateAPITest(TestCase):
    """Tests para endpoints de tipos de cambio"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            identification="API-TEST-002",
            username="apiuser2",
            email="api2@test.com",
            password="testpass123",
            role="user",
        )
        self.client.force_authenticate(user=self.user)

    def test_create_exchange_rate(self):
        """POST /api/utils/exchange-rates/"""
        data = {
            "base_currency": "COP",
            "currency": "USD",
            "year": 2025,
            "month": 1,
            "rate": "3750.0",
            "source": "test",
        }
        response = self.client.post("/api/utils/exchange-rates/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["currency"] == "USD"

    def test_list_exchange_rates(self):
        """GET /api/utils/exchange-rates/"""
        ExchangeRate.objects.create(
            base_currency="COP",
            currency="USD",
            year=2025,
            month=1,
            rate=Decimal("3750.0"),
        )
        response = self.client.get("/api/utils/exchange-rates/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_convert_endpoint(self):
        """GET /api/utils/exchange-rates/convert/"""
        ExchangeRate.objects.create(
            base_currency="COP",
            currency="USD",
            year=2025,
            month=1,
            rate=Decimal("4000.0"),
        )
        response = self.client.get(
            "/api/utils/exchange-rates/convert/",
            {"amount": "10000", "from": "USD", "to": "COP", "date": "2025-01-15"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["converted_amount"] == 40000000
        assert response.data["exchange_rate"] == 4000.0
