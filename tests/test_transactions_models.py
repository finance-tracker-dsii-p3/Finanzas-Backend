"""
Tests para transactions/models.py para aumentar coverage
"""

from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import Account
from categories.models import Category
from transactions.models import Transaction

User = get_user_model()


class TransactionModelTests(TestCase):
    """Tests para el modelo Transaction"""

    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            identification="12345678",
            username="testuser",
            email="test@example.com",
            password="testpass123",
            is_verified=True,
        )

        self.account = Account.objects.create(
            user=self.user,
            name="Test Account",
            account_type="asset",
            category="bank_account",
            current_balance=1000000,
            currency="COP",
        )

        self.category = Category.objects.create(
            user=self.user, name="Comida", type="expense", color="#DC2626"
        )

    def test_transaction_str(self):
        """Test: __str__ de Transaction"""
        transaction = Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            type=2,
            base_amount=10000,
            total_amount=10000,
            date=date.today(),
        )

        str_repr = str(transaction)
        assert str_repr is not None
        assert len(str_repr) > 0

    def test_transaction_save_calculates_totals(self):
        """Test: save() calcula totales automáticamente"""
        transaction = Transaction(
            user=self.user,
            origin_account=self.account,
            type=2,
            base_amount=10000,
            tax_percentage=19,
            date=date.today(),
        )

        # Antes de guardar, total_amount puede no estar calculado
        transaction.save()

        # Después de guardar, debe tener total_amount calculado
        assert transaction.total_amount is not None
        assert transaction.total_amount >= transaction.base_amount

    def test_transaction_save_without_tax(self):
        """Test: save() sin impuesto"""
        transaction = Transaction(
            user=self.user,
            origin_account=self.account,
            type=2,
            base_amount=10000,
            tax_percentage=None,
            date=date.today(),
        )

        transaction.save()

        # Sin impuesto, total_amount puede incluir GMF u otros cálculos
        assert transaction.total_amount is not None
        assert transaction.total_amount >= transaction.base_amount

    def test_transaction_get_type_display(self):
        """Test: get_type_display() retorna el nombre del tipo"""
        transaction = Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            type=1,  # Income
            base_amount=10000,
            total_amount=10000,
            date=date.today(),
        )

        type_display = transaction.get_type_display()
        assert type_display == "Income"

        transaction.type = 2  # Expense
        type_display = transaction.get_type_display()
        assert type_display == "Expense"

    def test_transaction_with_category(self):
        """Test: Crear transacción con categoría"""
        transaction = Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            category=self.category,
            type=2,
            base_amount=10000,
            total_amount=10000,
            date=date.today(),
        )

        assert transaction.category == self.category

    def test_transaction_without_category(self):
        """Test: Crear transacción sin categoría"""
        transaction = Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            category=None,
            type=3,  # Transfer
            base_amount=10000,
            total_amount=10000,
            date=date.today(),
        )

        assert transaction.category is None

    def test_transaction_save_calculates_gmf(self):
        """Test: save() calcula GMF para gastos"""
        transaction = Transaction(
            user=self.user,
            origin_account=self.account,
            type=2,  # Expense
            base_amount=1000000,  # 10,000.00 COP
            tax_percentage=19,
            date=date.today(),
        )

        transaction.save()

        # GMF debería ser 0.4% de (base_amount + taxed_amount)
        # base_amount = 1000000, taxed_amount = 190000
        # GMF = 0.004 * 1190000 = 4760 centavos
        assert transaction.gmf_amount > 0

    def test_transaction_save_with_gmf_exempt_account(self):
        """Test: save() no calcula GMF para cuentas exentas"""
        exempt_account = Account.objects.create(
            user=self.user,
            name="Cuenta Exenta",
            account_type="asset",
            category="bank_account",
            current_balance=1000000,
            currency="COP",
            gmf_exempt=True,
        )

        transaction = Transaction(
            user=self.user,
            origin_account=exempt_account,
            type=2,  # Expense
            base_amount=1000000,
            date=date.today(),
        )

        transaction.save()

        # GMF debería ser 0 para cuentas exentas
        assert transaction.gmf_amount == 0
