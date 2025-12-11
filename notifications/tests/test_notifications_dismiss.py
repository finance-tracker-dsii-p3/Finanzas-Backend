"""
Tests para funcionalidad de descartar notificaciones
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from budgets.models import Budget
from categories.models import Category
from notifications.engine import NotificationEngine
from notifications.models import Notification

User = get_user_model()


class NotificationDismissTestCase(TestCase):
    """Tests para funcionalidad de descartar notificaciones"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            identification="ID-DISMISS-1",
            username="dismissuser",
            email="dismiss@example.com",
            password="pass12345",
            role="user",
            is_verified=True,
        )
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        # Crear categoría y presupuesto para notificaciones
        self.category = Category.objects.create(name="Comida", type="expense", user=self.user)
        self.budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("1000000.00"),
            period=Budget.MONTHLY,
        )

        # Crear notificación de prueba
        self.notification = NotificationEngine.create_budget_warning(
            user=self.user,
            budget=self.budget,
            percentage=85,
            spent=Decimal("850000.00"),
            limit=Decimal("1000000.00"),
        )

    def test_mark_as_dismissed_model_method(self):
        """Test: Método mark_as_dismissed del modelo"""
        assert not self.notification.is_dismissed
        assert self.notification.dismissed_at is None

        self.notification.mark_as_dismissed()

        self.notification.refresh_from_db()
        assert self.notification.is_dismissed
        assert self.notification.dismissed_at is not None

    def test_dismiss_endpoint_success(self):
        """Test: Endpoint dismiss marca notificación como descartada"""
        url = f"/api/notifications/notifications/{self.notification.id}/dismiss/"
        response = self.client.post(url)

        assert response.status_code == 200
        assert "message" in response.data
        assert "notification" in response.data
        assert response.data["notification"]["is_dismissed"]

        # Verificar en BD
        self.notification.refresh_from_db()
        assert self.notification.is_dismissed
        assert self.notification.dismissed_at is not None

    def test_dismiss_endpoint_permission(self):
        """Test: Usuario no puede descartar notificación de otro usuario"""
        other_user = User.objects.create_user(
            identification="ID-OTHER-1",
            username="otheruser",
            email="other@example.com",
            password="pass12345",
        )
        other_token, _ = Token.objects.get_or_create(user=other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {other_token.key}")

        url = f"/api/notifications/notifications/{self.notification.id}/dismiss/"
        response = self.client.post(url)

        # DRF puede retornar 404 o 400 dependiendo de cómo se maneje el get_object
        assert response.status_code in [404, 403, 400]  # No encuentra, no tiene permiso o error

    def test_dismiss_all_endpoint(self):
        """Test: Endpoint dismiss_all descarta todas las notificaciones"""
        # Crear más notificaciones
        NotificationEngine.create_budget_exceeded(
            user=self.user,
            budget=self.budget,
            spent=Decimal("1100000.00"),
            limit=Decimal("1000000.00"),
        )

        url = "/api/notifications/notifications/dismiss_all/"
        response = self.client.post(url)

        assert response.status_code == 200
        assert "message" in response.data
        assert "updated_count" in response.data
        assert response.data["updated_count"] > 0

        # Verificar que todas están descartadas
        dismissed_count = Notification.objects.filter(user=self.user, is_dismissed=True).count()
        assert dismissed_count == response.data["updated_count"]

    def test_filter_dismissed_notifications(self):
        """Test: Filtrar notificaciones descartadas"""
        # Descartar una notificación
        self.notification.mark_as_dismissed()

        # Crear otra notificación no descartada
        NotificationEngine.create_budget_exceeded(
            user=self.user,
            budget=self.budget,
            spent=Decimal("1100000.00"),
            limit=Decimal("1000000.00"),
        )

        # Filtrar descartadas
        url = "/api/notifications/notifications/?dismissed=true"
        response = self.client.get(url)

        assert response.status_code == 200
        # Manejar paginación
        notifications = (
            response.data.get("results", response.data)
            if isinstance(response.data, dict)
            else response.data
        )
        assert len(notifications) > 0
        for notification in notifications:
            assert notification["is_dismissed"]

        # Filtrar no descartadas
        url = "/api/notifications/notifications/?dismissed=false"
        response = self.client.get(url)

        assert response.status_code == 200
        notifications = (
            response.data.get("results", response.data)
            if isinstance(response.data, dict)
            else response.data
        )
        for notification in notifications:
            assert not notification["is_dismissed"]

    def test_dismiss_and_read_independent(self):
        """Test: Descartar y leer son independientes"""
        # Marcar como leída
        self.notification.mark_as_read()
        assert self.notification.read
        assert not self.notification.is_dismissed

        # Descartar
        self.notification.mark_as_dismissed()
        self.notification.refresh_from_db()

        # Debe estar leída Y descartada
        assert self.notification.read
        assert self.notification.is_dismissed

    def test_dismiss_twice_idempotent(self):
        """Test: Descartar dos veces no causa error"""
        self.notification.mark_as_dismissed()
        first_dismissed_at = self.notification.dismissed_at

        # Descartar de nuevo
        self.notification.mark_as_dismissed()
        self.notification.refresh_from_db()

        # Debe mantener el mismo timestamp
        assert self.notification.dismissed_at == first_dismissed_at
        assert self.notification.is_dismissed
