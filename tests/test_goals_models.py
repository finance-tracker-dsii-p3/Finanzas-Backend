"""
Tests para goals/models.py para aumentar coverage
"""

from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase

from goals.models import Goal

User = get_user_model()


class GoalModelTests(TestCase):
    """Tests para el modelo Goal"""

    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            identification="12345678",
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

    def test_goal_str(self):
        """Test: __str__ de Goal"""
        goal = Goal.objects.create(
            user=self.user,
            name="Vacaciones",
            target_amount=5000000,
            saved_amount=2000000,
            date=date.today() + timedelta(days=180),
        )

        str_repr = str(goal)
        assert "Vacaciones" in str_repr
        assert "2000000" in str_repr
        assert "5000000" in str_repr

    def test_goal_get_progress_percentage(self):
        """Test: get_progress_percentage() calcula porcentaje correcto"""
        goal = Goal.objects.create(
            user=self.user,
            name="Meta",
            target_amount=1000000,
            saved_amount=500000,
            date=date.today() + timedelta(days=180),
        )

        progress = goal.get_progress_percentage()
        assert progress == 50.0

    def test_goal_get_progress_percentage_zero_target(self):
        """Test: get_progress_percentage() retorna 0 si target es 0"""
        goal = Goal.objects.create(
            user=self.user,
            name="Meta",
            target_amount=0,
            saved_amount=500000,
            date=date.today() + timedelta(days=180),
        )

        progress = goal.get_progress_percentage()
        assert progress == 0.0

    def test_goal_get_remaining_amount(self):
        """Test: get_remaining_amount() calcula monto restante"""
        goal = Goal.objects.create(
            user=self.user,
            name="Meta",
            target_amount=1000000,
            saved_amount=300000,
            date=date.today() + timedelta(days=180),
        )

        remaining = goal.get_remaining_amount()
        assert remaining == 700000

    def test_goal_get_remaining_amount_over_target(self):
        """Test: get_remaining_amount() retorna 0 si ya se alcanzó"""
        goal = Goal.objects.create(
            user=self.user,
            name="Meta",
            target_amount=1000000,
            saved_amount=1500000,
            date=date.today() + timedelta(days=180),
        )

        remaining = goal.get_remaining_amount()
        assert remaining == 0

    def test_goal_is_completed_false(self):
        """Test: is_completed() retorna False si no está completa"""
        goal = Goal.objects.create(
            user=self.user,
            name="Meta",
            target_amount=1000000,
            saved_amount=500000,
            date=date.today() + timedelta(days=180),
        )

        assert goal.is_completed() is False

    def test_goal_is_completed_true(self):
        """Test: is_completed() retorna True si está completa"""
        goal = Goal.objects.create(
            user=self.user,
            name="Meta",
            target_amount=1000000,
            saved_amount=1000000,
            date=date.today() + timedelta(days=180),
        )

        assert goal.is_completed() is True

    def test_goal_is_completed_over_target(self):
        """Test: is_completed() retorna True si excede el objetivo"""
        goal = Goal.objects.create(
            user=self.user,
            name="Meta",
            target_amount=1000000,
            saved_amount=1500000,
            date=date.today() + timedelta(days=180),
        )

        assert goal.is_completed() is True
