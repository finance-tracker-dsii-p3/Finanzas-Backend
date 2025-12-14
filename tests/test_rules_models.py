"""
Tests para rules/models.py para aumentar coverage
"""

from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import Account
from categories.models import Category
from rules.models import AutomaticRule
from transactions.models import Transaction

User = get_user_model()


class AutomaticRuleModelTests(TestCase):
    """Tests para el modelo AutomaticRule"""

    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            identification="12345678",
            username="testuser",
            email="test@example.com",
            password="testpass123",
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
            user=self.user, name="Transporte", type="expense", color="#DC2626"
        )

    def test_automatic_rule_str(self):
        """Test: __str__ de AutomaticRule"""
        rule = AutomaticRule.objects.create(
            user=self.user,
            name="Regla Uber",
            criteria_type=AutomaticRule.DESCRIPTION_CONTAINS,
            keyword="uber",
            action_type=AutomaticRule.ASSIGN_CATEGORY,
            target_category=self.category,
            is_active=True,
            order=1,
        )

        str_repr = str(rule)
        assert "Regla Uber" in str_repr

    def test_automatic_rule_clean_validates_keyword(self):
        """Test: clean() valida que keyword esté presente para DESCRIPTION_CONTAINS"""
        rule = AutomaticRule(
            user=self.user,
            name="Regla Test",
            criteria_type=AutomaticRule.DESCRIPTION_CONTAINS,
            keyword=None,  # Faltante
            action_type=AutomaticRule.ASSIGN_CATEGORY,
            target_category=self.category,
        )

        with self.assertRaises(ValidationError):
            rule.clean()

    def test_automatic_rule_clean_validates_target_category(self):
        """Test: clean() valida que target_category esté presente para ASSIGN_CATEGORY"""
        rule = AutomaticRule(
            user=self.user,
            name="Regla Test",
            criteria_type=AutomaticRule.DESCRIPTION_CONTAINS,
            keyword="test",
            action_type=AutomaticRule.ASSIGN_CATEGORY,
            target_category=None,  # Faltante
        )

        with self.assertRaises(ValidationError):
            rule.clean()

    def test_automatic_rule_clean_validates_category_user(self):
        """Test: clean() valida que la categoría pertenezca al usuario"""
        other_user = User.objects.create_user(
            identification="87654321",
            username="otheruser",
            email="other@example.com",
            password="testpass123",
        )
        other_category = Category.objects.create(
            user=other_user, name="Otra Categoría", type="expense"
        )

        rule = AutomaticRule(
            user=self.user,
            name="Regla Test",
            criteria_type=AutomaticRule.DESCRIPTION_CONTAINS,
            keyword="test",
            action_type=AutomaticRule.ASSIGN_CATEGORY,
            target_category=other_category,  # Categoría de otro usuario
        )

        with self.assertRaises(ValidationError):
            rule.clean()

    def test_automatic_rule_matches_transaction_by_description(self):
        """Test: matches_transaction() por descripción"""
        rule = AutomaticRule.objects.create(
            user=self.user,
            name="Regla Uber",
            criteria_type=AutomaticRule.DESCRIPTION_CONTAINS,
            keyword="uber",
            action_type=AutomaticRule.ASSIGN_CATEGORY,
            target_category=self.category,
            is_active=True,
            order=1,
        )

        transaction = Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            type=2,
            base_amount=10000,
            total_amount=10000,
            date=date.today(),
            description="Viaje en uber",
        )

        assert rule.matches_transaction(transaction) is True

    def test_automatic_rule_matches_transaction_by_type(self):
        """Test: matches_transaction() por tipo de transacción"""
        rule = AutomaticRule.objects.create(
            user=self.user,
            name="Regla Gastos",
            criteria_type=AutomaticRule.TRANSACTION_TYPE,
            target_transaction_type=2,  # Expense
            action_type=AutomaticRule.ASSIGN_CATEGORY,
            target_category=self.category,
            is_active=True,
            order=1,
        )

        transaction = Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            type=2,  # Expense
            base_amount=10000,
            total_amount=10000,
            date=date.today(),
        )

        assert rule.matches_transaction(transaction) is True

    def test_automatic_rule_apply_to_transaction(self):
        """Test: apply_to_transaction() asigna categoría"""
        rule = AutomaticRule.objects.create(
            user=self.user,
            name="Regla Uber",
            criteria_type=AutomaticRule.DESCRIPTION_CONTAINS,
            keyword="uber",
            action_type=AutomaticRule.ASSIGN_CATEGORY,
            target_category=self.category,
            is_active=True,
            order=1,
        )

        transaction = Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            type=2,
            base_amount=10000,
            total_amount=10000,
            date=date.today(),
            description="Viaje en uber",
        )

        rule.apply_to_transaction(transaction)

        transaction.refresh_from_db()
        assert transaction.category == self.category
        assert transaction.applied_rule == rule
