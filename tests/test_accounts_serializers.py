"""
Tests para serializers de cuentas (accounts/serializers.py)
Fase 1: Aumentar cobertura de tests
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import Account
from accounts.serializers import AccountCreateSerializer

User = get_user_model()


class AccountsSerializersTests(TestCase):
    """Tests para serializers de cuentas"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.user = User.objects.create_user(
            identification="12345678",
            username="testuser",
            email="test@example.com",
            password="testpass123",
            is_verified=True,
        )

        # Crear un request mock para el contexto
        from django.test import RequestFactory

        factory = RequestFactory()
        self.request = factory.get("/")
        self.request.user = self.user

    def test_validate_account_number_required_for_bank(self):
        """Test: Número de cuenta requerido para cuentas bancarias"""
        data = {
            "name": "Cuenta Banco",
            "account_type": Account.ASSET,
            "category": Account.BANK_ACCOUNT,
            "currency": "COP",
            "current_balance": "1000.00",
        }

        serializer = AccountCreateSerializer(data=data, context={"request": self.request})
        assert not serializer.is_valid()
        assert "account_number" in serializer.errors

    def test_validate_account_number_min_digits_cop(self):
        """Test: Validar mínimo de dígitos para COP"""
        data = {
            "name": "Cuenta Banco",
            "account_number": "123456789",  # Solo 9 dígitos, necesita 10
            "account_type": Account.ASSET,
            "category": Account.BANK_ACCOUNT,
            "currency": "COP",
            "current_balance": "1000.00",
        }

        serializer = AccountCreateSerializer(data=data, context={"request": self.request})
        assert not serializer.is_valid()
        assert "account_number" in serializer.errors

    def test_validate_account_number_min_digits_usd(self):
        """Test: Validar mínimo de dígitos para USD"""
        data = {
            "name": "Cuenta USD",
            "account_number": "123456",  # Solo 6 dígitos, necesita 7
            "account_type": Account.ASSET,
            "category": Account.BANK_ACCOUNT,
            "currency": "USD",
            "current_balance": "100.00",
        }

        serializer = AccountCreateSerializer(data=data, context={"request": self.request})
        assert not serializer.is_valid()
        assert "account_number" in serializer.errors

    def test_validate_account_number_min_digits_eur(self):
        """Test: Validar mínimo de dígitos para EUR"""
        data = {
            "name": "Cuenta EUR",
            "account_number": "1234567",  # Solo 7 dígitos, necesita 8
            "account_type": Account.ASSET,
            "category": Account.BANK_ACCOUNT,
            "currency": "EUR",
            "current_balance": "100.00",
        }

        serializer = AccountCreateSerializer(data=data, context={"request": self.request})
        assert not serializer.is_valid()
        assert "account_number" in serializer.errors

    def test_validate_account_number_optional_for_other(self):
        """Test: Número de cuenta opcional para categoría 'other'"""
        data = {
            "name": "Efectivo",
            "account_type": Account.ASSET,
            "category": Account.OTHER,
            "currency": "COP",
            "current_balance": "1000.00",
            # Sin account_number
        }

        serializer = AccountCreateSerializer(data=data, context={"request": self.request})
        assert serializer.is_valid()

    def test_validate_account_number_with_spaces(self):
        """Test: Validar que se ignoran espacios en número de cuenta"""
        data = {
            "name": "Cuenta Banco",
            "account_number": "1234 5678 9012",  # Con espacios, pero 12 dígitos
            "account_type": Account.ASSET,
            "category": Account.BANK_ACCOUNT,
            "currency": "COP",
            "current_balance": "1000.00",
        }

        serializer = AccountCreateSerializer(data=data, context={"request": self.request})
        assert serializer.is_valid()

    def test_validate_credit_card_positive_balance_error(self):
        """Test: Error al crear tarjeta de crédito con saldo positivo"""
        data = {
            "name": "Tarjeta Crédito",
            "account_number": "1234567890123",
            "account_type": Account.LIABILITY,
            "category": Account.CREDIT_CARD,
            "currency": "COP",
            "current_balance": "1000.00",  # Positivo, debería ser negativo
        }

        serializer = AccountCreateSerializer(data=data, context={"request": self.request})
        assert not serializer.is_valid()
        assert "current_balance" in serializer.errors

    def test_validate_credit_card_negative_credit_limit_error(self):
        """Test: Error al crear tarjeta con límite de crédito negativo"""
        data = {
            "name": "Tarjeta Crédito",
            "account_number": "1234567890123",
            "account_type": Account.LIABILITY,
            "category": Account.CREDIT_CARD,
            "currency": "COP",
            "current_balance": "-1000.00",
            "credit_limit": "-5000.00",  # Negativo, debería ser positivo
        }

        serializer = AccountCreateSerializer(data=data, context={"request": self.request})
        assert not serializer.is_valid()
        assert "credit_limit" in serializer.errors

    def test_validate_credit_card_zero_credit_limit_error(self):
        """Test: Error al crear tarjeta con límite de crédito cero"""
        data = {
            "name": "Tarjeta Crédito",
            "account_number": "1234567890123",
            "account_type": Account.LIABILITY,
            "category": Account.CREDIT_CARD,
            "currency": "COP",
            "current_balance": "-1000.00",
            "credit_limit": "0.00",  # Cero, debería ser positivo
        }

        serializer = AccountCreateSerializer(data=data, context={"request": self.request})
        assert not serializer.is_valid()
        assert "credit_limit" in serializer.errors

    def test_validate_expiration_date_non_credit_card_error(self):
        """Test: Error al usar expiration_date en cuenta no tarjeta"""
        data = {
            "name": "Cuenta Banco",
            "account_number": "1234567890123",
            "account_type": Account.ASSET,
            "category": Account.BANK_ACCOUNT,
            "currency": "COP",
            "current_balance": "1000.00",
            "expiration_date": "2025-12-31",  # No aplica para cuentas bancarias
        }

        serializer = AccountCreateSerializer(data=data, context={"request": self.request})
        assert not serializer.is_valid()
        assert "expiration_date" in serializer.errors

    def test_validate_credit_limit_non_credit_card_error(self):
        """Test: Error al usar credit_limit en cuenta no tarjeta"""
        data = {
            "name": "Cuenta Banco",
            "account_number": "1234567890123",
            "account_type": Account.ASSET,
            "category": Account.BANK_ACCOUNT,
            "currency": "COP",
            "current_balance": "1000.00",
            "credit_limit": "5000.00",  # No aplica para cuentas bancarias
        }

        serializer = AccountCreateSerializer(data=data, context={"request": self.request})
        assert not serializer.is_valid()
        assert "credit_limit" in serializer.errors

    def test_validate_liability_positive_balance_error(self):
        """Test: Error al crear pasivo con saldo positivo"""
        data = {
            "name": "Pasivo",
            "account_number": "1234567890123",
            "account_type": Account.LIABILITY,
            "category": Account.OTHER,
            "currency": "COP",
            "current_balance": "1000.00",  # Positivo, debería ser negativo o cero
        }

        serializer = AccountCreateSerializer(data=data, context={"request": self.request})
        assert not serializer.is_valid()
        assert "current_balance" in serializer.errors

    def test_validate_asset_negative_balance_error(self):
        """Test: Error al crear activo con saldo negativo"""
        data = {
            "name": "Activo",
            "account_number": "1234567890123",
            "account_type": Account.ASSET,
            "category": Account.BANK_ACCOUNT,
            "currency": "COP",
            "current_balance": "-1000.00",  # Negativo, no permitido para activos
        }

        serializer = AccountCreateSerializer(data=data, context={"request": self.request})
        assert not serializer.is_valid()
        assert "current_balance" in serializer.errors

    def test_validate_credit_card_sets_liability(self):
        """Test: Tarjeta de crédito automáticamente se establece como pasivo"""
        data = {
            "name": "Tarjeta Crédito",
            "account_number": "1234567890123",
            "account_type": Account.ASSET,  # Se establecerá como LIABILITY
            "category": Account.CREDIT_CARD,
            "currency": "COP",
            "current_balance": "-1000.00",
        }

        serializer = AccountCreateSerializer(data=data, context={"request": self.request})
        assert serializer.is_valid()
        assert serializer.validated_data["account_type"] == Account.LIABILITY

    def test_validate_account_number_other_category_with_valid_number(self):
        """Test: Categoría 'other' con número de cuenta válido"""
        data = {
            "name": "Efectivo con número",
            "account_number": "1234567890123",  # Opcional pero válido si se proporciona
            "account_type": Account.ASSET,
            "category": Account.OTHER,
            "currency": "COP",
            "current_balance": "1000.00",
        }

        serializer = AccountCreateSerializer(data=data, context={"request": self.request})
        assert serializer.is_valid()

    def test_validate_account_number_other_category_with_invalid_number(self):
        """Test: Categoría 'other' con número de cuenta inválido"""
        data = {
            "name": "Efectivo con número inválido",
            "account_number": "123",  # Muy corto
            "account_type": Account.ASSET,
            "category": Account.OTHER,
            "currency": "COP",
            "current_balance": "1000.00",
        }

        serializer = AccountCreateSerializer(data=data, context={"request": self.request})
        assert not serializer.is_valid()
        assert "account_number" in serializer.errors
