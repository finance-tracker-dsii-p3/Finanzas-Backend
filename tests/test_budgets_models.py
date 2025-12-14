"""
Tests para budgets/models.py para aumentar coverage
"""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from budgets.models import Budget
from categories.models import Category

User = get_user_model()


class BudgetModelTests(TestCase):
    """Tests para el modelo Budget"""

    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            identification="12345678",
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        self.category = Category.objects.create(
            user=self.user, name="Comida", type="expense", color="#DC2626"
        )

    def test_budget_str(self):
        """Test: __str__ de Budget"""
        budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("100000.00"),
            period=Budget.MONTHLY,
            start_date=date(2025, 1, 1),
            currency="COP",
        )

        str_repr = str(budget)
        assert "Comida" in str_repr

    def test_budget_clean_validates_category_user(self):
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

        budget = Budget(
            user=self.user,
            category=other_category,
            amount=Decimal("100000.00"),
            period=Budget.MONTHLY,
            start_date=date(2025, 1, 1),
        )

        with self.assertRaises(ValidationError):
            budget.clean()

    def test_budget_clean_validates_alert_threshold(self):
        """Test: clean() valida que alert_threshold no sea mayor a 100"""
        budget = Budget(
            user=self.user,
            category=self.category,
            amount=Decimal("100000.00"),
            period=Budget.MONTHLY,
            start_date=date(2025, 1, 1),
            alert_threshold=Decimal("150.00"),  # Mayor a 100
        )

        with self.assertRaises(ValidationError):
            budget.clean()

    def test_budget_get_period_dates_monthly(self):
        """Test: get_period_dates() para período mensual"""
        budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("100000.00"),
            period=Budget.MONTHLY,
            start_date=date(2025, 1, 15),
            currency="COP",
        )

        start, end = budget.get_period_dates(date(2025, 1, 20))
        assert start == date(2025, 1, 1)
        assert end == date(2025, 1, 31)

    def test_budget_get_period_dates_yearly(self):
        """Test: get_period_dates() para período anual"""
        budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("1000000.00"),
            period=Budget.YEARLY,
            start_date=date(2025, 6, 15),
            currency="COP",
        )

        start, end = budget.get_period_dates(date(2025, 6, 20))
        assert start == date(2025, 1, 1)
        assert end == date(2025, 12, 31)
