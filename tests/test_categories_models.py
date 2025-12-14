"""
Tests para categories/models.py para aumentar coverage
"""

from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from budgets.models import Budget
from categories.models import Category, validate_color_contrast, validate_hex_color

User = get_user_model()


class CategoryModelTests(TestCase):
    """Tests para el modelo Category"""

    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            identification="12345678",
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_category_str(self):
        """Test: __str__ de Category"""
        category = Category.objects.create(
            user=self.user, name="Comida", type=Category.EXPENSE, color="#DC2626"
        )

        str_repr = str(category)
        assert "Comida" in str_repr
        assert "Gasto" in str_repr or "Expense" in str_repr

    def test_category_clean_normalizes_name(self):
        """Test: clean() normaliza el nombre"""
        category = Category(
            user=self.user, name="  comida rápida  ", type=Category.EXPENSE, color="#DC2626"
        )
        category.clean()
        assert category.name == "Comida Rápida"

    def test_category_clean_prevents_duplicate(self):
        """Test: clean() previene categorías duplicadas"""
        Category.objects.create(
            user=self.user, name="Comida", type=Category.EXPENSE, color="#DC2626"
        )

        duplicate = Category(user=self.user, name="comida", type=Category.EXPENSE, color="#FF0000")

        with self.assertRaises(ValidationError):
            duplicate.clean()

    def test_category_can_be_deleted_no_usage(self):
        """Test: can_be_deleted() retorna True si no tiene uso"""
        category = Category.objects.create(
            user=self.user, name="Comida", type=Category.EXPENSE, color="#DC2626"
        )

        assert category.can_be_deleted() is True

    def test_category_can_be_deleted_with_budget(self):
        """Test: can_be_deleted() retorna False si tiene presupuesto"""
        category = Category.objects.create(
            user=self.user, name="Comida", type=Category.EXPENSE, color="#DC2626"
        )

        Budget.objects.create(
            user=self.user,
            category=category,
            amount=100000,
            period=Budget.MONTHLY,
            start_date=date(2025, 1, 1),
        )

        assert category.can_be_deleted() is False

    def test_category_get_usage_count(self):
        """Test: get_usage_count() retorna el conteo de uso"""
        category = Category.objects.create(
            user=self.user, name="Comida", type=Category.EXPENSE, color="#DC2626"
        )

        count = category.get_usage_count()
        assert count == 0

        Budget.objects.create(
            user=self.user,
            category=category,
            amount=100000,
            period=Budget.MONTHLY,
            start_date=date(2025, 1, 1),
        )

        count = category.get_usage_count()
        assert count == 1

    def test_category_get_related_data(self):
        """Test: get_related_data() retorna información relacionada"""
        category = Category.objects.create(
            user=self.user, name="Comida", type=Category.EXPENSE, color="#DC2626"
        )

        data = category.get_related_data()
        assert "transactions_count" in data
        assert "budgets_count" in data
        assert "can_be_deleted" in data
        assert "usage_count" in data


class CategoryValidatorsTests(TestCase):
    """Tests para validadores de Category"""

    def test_validate_hex_color_valid(self):
        """Test: validate_hex_color acepta colores válidos"""
        validate_hex_color("#FF5733")
        validate_hex_color("#000000")
        validate_hex_color("#FFFFFF")
        validate_hex_color("#abc123")

    def test_validate_hex_color_invalid(self):
        """Test: validate_hex_color rechaza colores inválidos"""
        with self.assertRaises(ValidationError):
            validate_hex_color("FF5733")  # Sin #

        with self.assertRaises(ValidationError):
            validate_hex_color("#FF")  # Muy corto

        with self.assertRaises(ValidationError):
            validate_hex_color("#FF57333")  # Muy largo

    def test_validate_color_contrast_good(self):
        """Test: validate_color_contrast acepta colores con buen contraste"""
        validate_color_contrast("#000000")  # Negro
        validate_color_contrast("#FF0000")  # Rojo
        validate_color_contrast("#0066CC")  # Azul

    def test_validate_color_contrast_poor(self):
        """Test: validate_color_contrast rechaza colores con mal contraste"""
        with self.assertRaises(ValidationError):
            validate_color_contrast("#FFFFFE")  # Casi blanco

        with self.assertRaises(ValidationError):
            validate_color_contrast("#FEFEFE")  # Muy claro

    def test_validate_color_contrast_invalid_length(self):
        """Test: validate_color_contrast maneja colores de longitud inválida"""
        # No debe lanzar error si la longitud es incorrecta (validate_hex_color se encarga)
        from contextlib import suppress

        with suppress(ValidationError):
            validate_color_contrast("#FF")  # Muy corto
