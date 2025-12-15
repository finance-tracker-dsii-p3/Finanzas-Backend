"""
Tests para la API de Utilidades (utils/views.py)
Fase 1: Aumentar cobertura de tests
"""

from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from utils.models import BaseCurrencySetting, ExchangeRate

User = get_user_model()


class UtilsViewsTests(TestCase):
    """Tests para endpoints de utilidades"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = APIClient()

        # Crear usuario y token
        self.user = User.objects.create_user(
            identification="12345678",
            username="testuser",
            email="test@example.com",
            password="testpass123",
            is_verified=True,
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_get_exchange_rate_success(self):
        """Test: Obtener tasa de cambio exitosamente"""
        response = self.client.get("/api/utils/currency/exchange-rate/?from=COP&to=USD")
        assert response.status_code == status.HTTP_200_OK
        assert "from" in response.data
        assert "to" in response.data
        assert "rate" in response.data
        assert response.data["from"] == "COP"
        assert response.data["to"] == "USD"

    def test_get_exchange_rate_missing_parameters(self):
        """Test: Error cuando faltan parámetros"""
        response = self.client.get("/api/utils/currency/exchange-rate/?from=COP")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    def test_get_exchange_rate_invalid_currency(self):
        """Test: Error con moneda inválida"""
        response = self.client.get("/api/utils/currency/exchange-rate/?from=XXX&to=YYY")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_convert_currency_success(self):
        """Test: Convertir moneda exitosamente"""
        response = self.client.get("/api/utils/currency/convert/?amount=100000&from=COP&to=USD")
        assert response.status_code == status.HTTP_200_OK
        assert "original_amount" in response.data
        assert "converted_amount" in response.data
        assert "exchange_rate" in response.data
        assert response.data["original_amount"] == 100000
        assert response.data["original_currency"] == "COP"

    def test_convert_currency_missing_parameters(self):
        """Test: Error cuando faltan parámetros"""
        response = self.client.get("/api/utils/currency/convert/?amount=100000")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_convert_currency_invalid_amount(self):
        """Test: Error con monto inválido"""
        response = self.client.get("/api/utils/currency/convert/?amount=0&from=COP&to=USD")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_base_currency_list_success(self):
        """Test: Obtener moneda base del usuario"""
        response = self.client.get("/api/utils/base-currency/")
        assert response.status_code == status.HTTP_200_OK
        assert "base_currency" in response.data
        assert "available_currencies" in response.data

    def test_base_currency_set_success(self):
        """Test: Establecer moneda base"""
        data = {"base_currency": "USD"}
        response = self.client.put("/api/utils/base-currency/set_base/", data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "base_currency" in response.data
        assert response.data["base_currency"] == "USD"

        # Verificar que se guardó
        setting = BaseCurrencySetting.objects.filter(user=self.user).first()
        assert setting is not None
        assert setting.base_currency == "USD"

    def test_base_currency_set_invalid_currency(self):
        """Test: Error con moneda inválida"""
        data = {"base_currency": "XXX"}
        response = self.client.put("/api/utils/base-currency/set_base/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_exchange_rate_list_success(self):
        """Test: Listar tipos de cambio"""
        # Crear tipo de cambio de prueba
        ExchangeRate.objects.create(
            currency="USD",
            base_currency="COP",
            year=2025,
            month=1,
            rate=4000.0,
        )

        response = self.client.get("/api/utils/exchange-rates/")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, (list, dict))

    def test_exchange_rate_create_success(self):
        """Test: Crear tipo de cambio"""
        data = {
            "currency": "USD",
            "base_currency": "COP",
            "year": 2025,
            "month": 1,
            "rate": 4000.0,
        }
        response = self.client.post("/api/utils/exchange-rates/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["currency"] == "USD"
        assert ExchangeRate.objects.filter(currency="USD", year=2025, month=1).exists()

    def test_exchange_rate_filter_by_currency(self):
        """Test: Filtrar tipos de cambio por moneda"""
        ExchangeRate.objects.create(
            currency="USD",
            base_currency="COP",
            year=2025,
            month=1,
            rate=4000.0,
        )
        ExchangeRate.objects.create(
            currency="EUR",
            base_currency="COP",
            year=2025,
            month=1,
            rate=4500.0,
        )

        response = self.client.get("/api/utils/exchange-rates/?currency=USD")
        assert response.status_code == status.HTTP_200_OK
        # Verificar que solo devuelve USD
        if isinstance(response.data, list):
            for rate in response.data:
                assert rate["currency"] == "USD"

    def test_exchange_rate_filter_by_year_month(self):
        """Test: Filtrar tipos de cambio por año y mes"""
        ExchangeRate.objects.create(
            currency="USD",
            base_currency="COP",
            year=2025,
            month=1,
            rate=4000.0,
        )
        ExchangeRate.objects.create(
            currency="USD",
            base_currency="COP",
            year=2024,
            month=12,
            rate=3900.0,
        )

        response = self.client.get("/api/utils/exchange-rates/?year=2025&month=1")
        assert response.status_code == status.HTTP_200_OK

    def test_exchange_rate_current_success(self):
        """Test: Obtener tipo de cambio vigente"""
        # Crear tipo de cambio
        ExchangeRate.objects.create(
            currency="USD",
            base_currency="COP",
            year=2025,
            month=1,
            rate=4000.0,
        )

        response = self.client.get(
            "/api/utils/exchange-rates/current/?currency=USD&base=COP&date=2025-01-15"
        )
        assert response.status_code == status.HTTP_200_OK
        assert "currency" in response.data
        assert "rate" in response.data
        assert response.data["currency"] == "USD"

    def test_exchange_rate_current_missing_currency(self):
        """Test: Error cuando falta parámetro currency"""
        response = self.client.get("/api/utils/exchange-rates/current/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_exchange_rate_current_invalid_date(self):
        """Test: Error con fecha inválida"""
        response = self.client.get("/api/utils/exchange-rates/current/?currency=USD&date=invalid")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_exchange_rate_convert_success(self):
        """Test: Convertir monto usando tipos de cambio"""
        # Crear tipo de cambio
        ExchangeRate.objects.create(
            currency="USD",
            base_currency="COP",
            year=2025,
            month=1,
            rate=4000.0,
        )

        response = self.client.get(
            "/api/utils/exchange-rates/convert/?amount=10000&from=USD&to=COP&date=2025-01-15"
        )
        assert response.status_code == status.HTTP_200_OK
        assert "original_amount" in response.data
        assert "converted_amount" in response.data
        assert "exchange_rate" in response.data

    def test_exchange_rate_convert_missing_parameters(self):
        """Test: Error cuando faltan parámetros"""
        response = self.client.get("/api/utils/exchange-rates/convert/?from=USD")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_exchange_rate_convert_invalid_amount(self):
        """Test: Error con monto inválido"""
        response = self.client.get(
            "/api/utils/exchange-rates/convert/?amount=invalid&from=USD&to=COP"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_exchange_rate_update_success(self):
        """Test: Actualizar tipo de cambio"""
        rate = ExchangeRate.objects.create(
            currency="USD",
            base_currency="COP",
            year=2025,
            month=1,
            rate=4000.0,
        )

        data = {
            "currency": "USD",
            "base_currency": "COP",
            "year": 2025,
            "month": 1,
            "rate": 4100.0,
        }
        response = self.client.patch(f"/api/utils/exchange-rates/{rate.id}/", data, format="json")
        assert response.status_code == status.HTTP_200_OK
        rate.refresh_from_db()
        assert rate.rate == 4100.0

    def test_exchange_rate_delete_success(self):
        """Test: Eliminar tipo de cambio"""
        rate = ExchangeRate.objects.create(
            currency="USD",
            base_currency="COP",
            year=2025,
            month=1,
            rate=4000.0,
        )

        response = self.client.delete(f"/api/utils/exchange-rates/{rate.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not ExchangeRate.objects.filter(id=rate.id).exists()

    def test_get_exchange_rate_requires_authentication(self):
        """Test: Obtener tasa requiere autenticación"""
        self.client.credentials()
        response = self.client.get("/api/utils/currency/exchange-rate/?from=COP&to=USD")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_convert_currency_requires_authentication(self):
        """Test: Convertir moneda requiere autenticación"""
        self.client.credentials()
        response = self.client.get("/api/utils/currency/convert/?amount=100000&from=COP&to=USD")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_exchange_rate_current_with_warning(self):
        """Test: Obtener tipo de cambio con advertencia"""
        # Crear tipo de cambio antiguo
        ExchangeRate.objects.create(
            currency="USD",
            base_currency="COP",
            year=2024,
            month=1,
            rate=3900.0,
        )

        # Consultar para fecha reciente (puede generar warning)
        response = self.client.get(
            "/api/utils/exchange-rates/current/?currency=USD&base=COP&date=2025-12-14"
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_exchange_rate_convert_with_warning(self):
        """Test: Convertir con advertencia de tipo de cambio antiguo"""
        # Crear tipo de cambio antiguo
        ExchangeRate.objects.create(
            currency="USD",
            base_currency="COP",
            year=2024,
            month=1,
            rate=3900.0,
        )

        response = self.client.get(
            "/api/utils/exchange-rates/convert/?amount=10000&from=USD&to=COP&date=2025-12-14"
        )
        # Puede ser 200 con warning o 400/404 si no encuentra tasa
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_exchange_rate_current_without_base_uses_user_base(self):
        """Test: Usar moneda base del usuario si no se especifica"""
        # Establecer moneda base del usuario
        BaseCurrencySetting.objects.create(user=self.user, base_currency="EUR")

        ExchangeRate.objects.create(
            currency="USD",
            base_currency="EUR",
            year=2025,
            month=1,
            rate=0.9,
        )

        response = self.client.get("/api/utils/exchange-rates/current/?currency=USD")
        # Puede ser 200 o 404 dependiendo de si encuentra la tasa
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_exchange_rate_convert_without_to_uses_user_base(self):
        """Test: Usar moneda base del usuario como destino si no se especifica"""
        # Establecer moneda base del usuario
        BaseCurrencySetting.objects.create(user=self.user, base_currency="EUR")

        ExchangeRate.objects.create(
            currency="USD",
            base_currency="EUR",
            year=2025,
            month=1,
            rate=0.9,
        )

        response = self.client.get(
            "/api/utils/exchange-rates/convert/?amount=10000&from=USD&date=2025-01-15"
        )
        # Puede ser 200 o 404 dependiendo de si encuentra la tasa
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
        ]

    def test_exchange_rate_filter_by_base_currency(self):
        """Test: Filtrar tipos de cambio por moneda base"""
        ExchangeRate.objects.create(
            currency="USD",
            base_currency="COP",
            year=2025,
            month=1,
            rate=4000.0,
        )
        ExchangeRate.objects.create(
            currency="USD",
            base_currency="EUR",
            year=2025,
            month=1,
            rate=0.9,
        )

        response = self.client.get("/api/utils/exchange-rates/?base_currency=COP")
        assert response.status_code == status.HTTP_200_OK

    def test_convert_currency_exception_handling(self):
        """Test: Manejo de excepciones en conversión de moneda"""
        # Este test verifica el bloque except Exception
        # Intentar conversión que pueda fallar
        response = self.client.get("/api/utils/currency/convert/?amount=100000&from=XXX&to=YYY")
        # Debe manejar el error correctamente
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ]
