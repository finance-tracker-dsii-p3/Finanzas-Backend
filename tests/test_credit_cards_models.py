"""
Tests para credit_cards/models.py para aumentar coverage
"""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import Account
from categories.models import Category
from credit_cards.models import InstallmentPayment, InstallmentPlan
from transactions.models import Transaction

User = get_user_model()


class InstallmentPlanModelTests(TestCase):
    """Tests para el modelo InstallmentPlan"""

    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            identification="12345678",
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        self.bank_account = Account.objects.create(
            user=self.user,
            name="Banco",
            account_type=Account.ASSET,
            category=Account.BANK_ACCOUNT,
            current_balance=1000000,
            currency="COP",
        )

        self.credit_card = Account.objects.create(
            user=self.user,
            name="Tarjeta Crédito",
            account_type=Account.LIABILITY,
            category=Account.CREDIT_CARD,
            current_balance=-100000,
            currency="COP",
        )

        self.purchase_category = Category.objects.create(
            user=self.user, name="Compras", type="expense"
        )

        self.financing_category = Category.objects.create(
            user=self.user, name="Financiación", type="expense"
        )

        self.purchase_transaction = Transaction.objects.create(
            user=self.user,
            origin_account=self.credit_card,
            category=self.purchase_category,
            type=2,
            base_amount=1200000,
            total_amount=1200000,
            date=date.today(),
        )

    def test_installment_plan_clean_validates_credit_card(self):
        """Test: clean() valida que la cuenta sea tarjeta de crédito"""
        plan = InstallmentPlan(
            user=self.user,
            credit_card_account=self.bank_account,  # No es tarjeta de crédito
            purchase_transaction=self.purchase_transaction,
            purchase_amount=1200000,
            number_of_installments=12,
            interest_rate=Decimal("2.00"),
            start_date=date.today(),
            financing_category=self.financing_category,
        )

        with self.assertRaises(ValidationError):
            plan.clean()

    def test_installment_plan_clean_validates_financing_category(self):
        """Test: clean() valida que la categoría de financiamiento sea de gasto"""
        income_category = Category.objects.create(user=self.user, name="Ingresos", type="income")

        plan = InstallmentPlan(
            user=self.user,
            credit_card_account=self.credit_card,
            purchase_transaction=self.purchase_transaction,
            purchase_amount=1200000,
            number_of_installments=12,
            interest_rate=Decimal("2.00"),
            start_date=date.today(),
            financing_category=income_category,  # No es de gasto
        )

        with self.assertRaises(ValidationError):
            plan.clean()
