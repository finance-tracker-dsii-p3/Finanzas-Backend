"""
Tests para serializers de cuentas (accounts/serializers.py)
Fase 1: Aumentar cobertura de tests
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import Account
from accounts.serializers import (
    AccountCreateSerializer,
    AccountDetailSerializer,
    AccountListSerializer,
    AccountUpdateSerializer,
)

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

    def test_account_list_serializer_credit_card_details(self):
        """Test: AccountListSerializer incluye detalles de tarjeta de crédito"""
        credit_card = Account.objects.create(
            user=self.user,
            name="Tarjeta Crédito",
            account_number="1234567890123",
            account_type=Account.LIABILITY,
            category=Account.CREDIT_CARD,
            currency="COP",
            current_balance=Decimal("-500000.00"),
            credit_limit=Decimal("2000000.00"),
        )

        serializer = AccountListSerializer(credit_card)
        data = serializer.data
        assert "credit_card_details" in data
        assert data["credit_card_details"] is not None

    def test_account_list_serializer_non_credit_card_no_details(self):
        """Test: AccountListSerializer no incluye detalles para cuentas no tarjeta"""
        bank_account = Account.objects.create(
            user=self.user,
            name="Banco Principal",
            account_number="1234567890123",
            account_type=Account.ASSET,
            category=Account.BANK_ACCOUNT,
            currency="COP",
            current_balance=Decimal("1000000.00"),
        )

        serializer = AccountListSerializer(bank_account)
        data = serializer.data
        assert "credit_card_details" in data
        assert data["credit_card_details"] is None

    def test_account_detail_serializer_credit_card_details(self):
        """Test: AccountDetailSerializer incluye detalles de tarjeta de crédito"""
        credit_card = Account.objects.create(
            user=self.user,
            name="Tarjeta Crédito",
            account_number="1234567890123",
            account_type=Account.LIABILITY,
            category=Account.CREDIT_CARD,
            currency="COP",
            current_balance=Decimal("-500000.00"),
            credit_limit=Decimal("2000000.00"),
        )

        serializer = AccountDetailSerializer(credit_card)
        data = serializer.data
        assert "credit_card_details" in data
        assert data["credit_card_details"] is not None

    def test_account_update_serializer_change_account_type_with_balance_error(self):
        """Test: Error al cambiar tipo de cuenta cuando tiene saldo"""
        account = Account.objects.create(
            user=self.user,
            name="Cuenta Banco",
            account_number="1234567890123",
            account_type=Account.ASSET,
            category=Account.BANK_ACCOUNT,
            currency="COP",
            current_balance=Decimal("1000.00"),
        )

        serializer = AccountUpdateSerializer(
            instance=account,
            data={"account_type": Account.LIABILITY},
            context={"request": self.request},
        )
        assert not serializer.is_valid()
        assert "account_type" in serializer.errors

    def test_account_update_serializer_change_currency_with_balance_error(self):
        """Test: Error al cambiar moneda cuando tiene saldo"""
        account = Account.objects.create(
            user=self.user,
            name="Cuenta Banco",
            account_number="1234567890123",
            account_type=Account.ASSET,
            category=Account.BANK_ACCOUNT,
            currency="COP",
            current_balance=Decimal("1000.00"),
        )

        serializer = AccountUpdateSerializer(
            instance=account,
            data={"currency": "USD"},
            context={"request": self.request},
        )
        assert not serializer.is_valid()
        assert "currency" in serializer.errors

    def test_account_update_serializer_credit_card_validation(self):
        """Test: Validación de tarjeta de crédito en actualización"""
        credit_card = Account.objects.create(
            user=self.user,
            name="Tarjeta Crédito",
            account_number="1234567890123",
            account_type=Account.LIABILITY,
            category=Account.CREDIT_CARD,
            currency="COP",
            current_balance=Decimal("-500000.00"),
            credit_limit=Decimal("2000000.00"),
        )

        from datetime import date

        serializer = AccountUpdateSerializer(
            instance=credit_card,
            data={"expiration_date": date(2025, 12, 31)},
            context={"request": self.request},
        )
        assert serializer.is_valid(), serializer.errors

    def test_account_update_serializer_negative_credit_limit_error(self):
        """Test: Error al actualizar límite de crédito a negativo"""
        credit_card = Account.objects.create(
            user=self.user,
            name="Tarjeta Crédito",
            account_number="1234567890123",
            account_type=Account.LIABILITY,
            category=Account.CREDIT_CARD,
            currency="COP",
            current_balance=Decimal("-500000.00"),
            credit_limit=Decimal("2000000.00"),
        )

        serializer = AccountUpdateSerializer(
            instance=credit_card,
            data={"credit_limit": Decimal("-1000.00")},
            context={"request": self.request},
        )
        assert not serializer.is_valid()
        assert "credit_limit" in serializer.errors

    def test_account_update_serializer_duplicate_name_error(self):
        """Test: Error al actualizar con nombre duplicado"""
        account1 = Account.objects.create(
            user=self.user,
            name="Cuenta 1",
            account_number="1234567890123",
            account_type=Account.ASSET,
            category=Account.BANK_ACCOUNT,
            currency="COP",
            current_balance=Decimal("1000.00"),
        )

        account2 = Account.objects.create(
            user=self.user,
            name="Cuenta 2",
            account_number="9876543210987",
            account_type=Account.ASSET,
            category=Account.BANK_ACCOUNT,
            currency="COP",
            current_balance=Decimal("2000.00"),
        )

        serializer = AccountUpdateSerializer(
            instance=account2,
            data={"name": "Cuenta 1"},
            context={"request": self.request},
        )
        assert not serializer.is_valid()
        assert "name" in serializer.errors

    def test_account_update_serializer_same_name_allowed(self):
        """Test: Permitir mantener el mismo nombre"""
        account = Account.objects.create(
            user=self.user,
            name="Cuenta Banco",
            account_number="1234567890123",
            account_type=Account.ASSET,
            category=Account.BANK_ACCOUNT,
            currency="COP",
            current_balance=Decimal("1000.00"),
        )

        serializer = AccountUpdateSerializer(
            instance=account,
            data={"name": "Cuenta Banco"},
            context={"request": self.request},
        )
        assert serializer.is_valid(), serializer.errors

    def test_account_balance_update_serializer(self):
        """Test: AccountBalanceUpdateSerializer valida new_balance"""
        from accounts.serializers import AccountBalanceUpdateSerializer

        # Crear cuenta para el contexto
        account = Account.objects.create(
            user=self.user,
            name="Test Account",
            account_number="1234567890123",
            account_type=Account.ASSET,
            category=Account.BANK_ACCOUNT,
            current_balance=Decimal("1000.00"),
            currency="COP",
        )

        serializer = AccountBalanceUpdateSerializer(
            data={"new_balance": "2000.00"}, context={"account": account}
        )
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["new_balance"] == Decimal("2000.00")

    def test_account_balance_update_serializer_with_reason(self):
        """Test: AccountBalanceUpdateSerializer con razón opcional"""
        from accounts.serializers import AccountBalanceUpdateSerializer

        account = Account.objects.create(
            user=self.user,
            name="Test Account",
            account_number="1234567890123",
            account_type=Account.ASSET,
            category=Account.BANK_ACCOUNT,
            current_balance=Decimal("1000.00"),
            currency="COP",
        )

        serializer = AccountBalanceUpdateSerializer(
            data={"new_balance": "2000.00", "reason": "Ajuste manual"},
            context={"account": account},
        )
        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["reason"] == "Ajuste manual"

    def test_account_balance_update_serializer_liability_positive_error(self):
        """Test: Error al actualizar pasivo con saldo positivo"""
        from accounts.serializers import AccountBalanceUpdateSerializer

        liability_account = Account.objects.create(
            user=self.user,
            name="Pasivo",
            account_number="1234567890123",
            account_type=Account.LIABILITY,
            category=Account.OTHER,
            current_balance=Decimal("-1000.00"),
            currency="COP",
        )

        serializer = AccountBalanceUpdateSerializer(
            data={"new_balance": "1000.00"}, context={"account": liability_account}
        )
        assert not serializer.is_valid()
        assert "new_balance" in serializer.errors

    def test_account_balance_update_serializer_asset_negative_error(self):
        """Test: Error al actualizar activo con saldo negativo"""
        from accounts.serializers import AccountBalanceUpdateSerializer

        asset_account = Account.objects.create(
            user=self.user,
            name="Activo",
            account_number="1234567890123",
            account_type=Account.ASSET,
            category=Account.BANK_ACCOUNT,
            current_balance=Decimal("1000.00"),
            currency="COP",
        )

        serializer = AccountBalanceUpdateSerializer(
            data={"new_balance": "-1000.00"}, context={"account": asset_account}
        )
        assert not serializer.is_valid()
        assert "new_balance" in serializer.errors

    def test_account_summary_serializer(self):
        """Test: AccountSummarySerializer serializa datos de resumen"""
        from accounts.serializers import AccountSummarySerializer

        summary_data = {
            "total_assets": Decimal("1000000.00"),
            "total_liabilities": Decimal("500000.00"),
            "net_worth": Decimal("500000.00"),
            "accounts_count": 2,
            "active_accounts_count": 2,
            "balances_by_currency": {
                "COP": {
                    "assets": Decimal("1000000.00"),
                    "liabilities": Decimal("500000.00"),
                    "net": Decimal("500000.00"),
                }
            },
            "accounts_by_category": {"Banco": {"count": 1, "balance": Decimal("1000000.00")}},
        }

        serializer = AccountSummarySerializer(data=summary_data)
        assert serializer.is_valid(), serializer.errors
