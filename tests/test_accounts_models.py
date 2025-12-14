"""
Tests para accounts/models.py para aumentar coverage
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import Account, AccountOption, AccountOptionType

User = get_user_model()


class AccountModelTests(TestCase):
    """Tests para el modelo Account"""

    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            identification="12345678",
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_account_str(self):
        """Test: __str__ de Account"""
        account = Account.objects.create(
            user=self.user,
            name="Cuenta Test",
            account_type="asset",
            category="bank_account",
            current_balance=Decimal("1000000.00"),
            currency="COP",
        )

        str_repr = str(account)
        assert "Cuenta Test" in str_repr
        assert "COP" in str_repr or "Pesos" in str_repr

    def test_account_balance_for_totals_asset(self):
        """Test: balance_for_totals para cuenta de activo"""
        account = Account.objects.create(
            user=self.user,
            name="Cuenta Activo",
            account_type=Account.ASSET,
            category="bank_account",
            current_balance=Decimal("1000000.00"),
            currency="COP",
        )

        balance = account.balance_for_totals
        assert balance == Decimal("1000000.00")

    def test_account_balance_for_totals_liability(self):
        """Test: balance_for_totals para cuenta de pasivo"""
        account = Account.objects.create(
            user=self.user,
            name="Tarjeta Crédito",
            account_type=Account.LIABILITY,
            category="credit_card",
            current_balance=Decimal("-500000.00"),  # Deuda
            currency="COP",
        )

        balance = account.balance_for_totals
        # Debe retornar el valor absoluto
        assert balance == Decimal("500000.00")

    def test_account_can_be_deleted(self):
        """Test: can_be_deleted() retorna True"""
        account = Account.objects.create(
            user=self.user,
            name="Cuenta Test",
            account_type="asset",
            category="bank_account",
            current_balance=Decimal("1000000.00"),
            currency="COP",
        )

        assert account.can_be_deleted() is True


class AccountOptionModelTests(TestCase):
    """Tests para el modelo AccountOption"""

    def test_account_option_str(self):
        """Test: __str__ de AccountOption"""
        option = AccountOption.objects.create(
            name="Bancolombia",
            option_type=AccountOptionType.BANK,
            is_active=True,
        )

        str_repr = str(option)
        assert "Bancolombia" in str_repr
        assert "Banco" in str_repr
