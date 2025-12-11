"""
Tests completos para API de notificaciones
Cubre todos los endpoints y casos de uso
"""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from accounts.models import Account
from bills.models import Bill
from budgets.models import Budget
from categories.models import Category
from notifications.engine import NotificationEngine
from notifications.models import CustomReminder, Notification
from users.models import UserNotificationPreferences
from vehicles.models import SOAT, Vehicle

User = get_user_model()


class NotificationsApiCompleteTestCase(TestCase):
    """Tests completos para API de notificaciones"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            identification="ID-API-1",
            username="apiuser",
            email="api@example.com",
            password="pass12345",
            role="user",
            is_verified=True,
        )
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        # Crear preferencias
        UserNotificationPreferences.objects.create(
            user=self.user,
            timezone="America/Bogota",
            language="es",
            enable_budget_alerts=True,
            enable_bill_reminders=True,
            enable_soat_reminders=True,
            enable_month_end_reminders=True,
            enable_custom_reminders=True,
        )

        # Crear datos de prueba
        self.category = Category.objects.create(name="Comida", type="expense", user=self.user)
        self.budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal("1000000.00"),
            period=Budget.MONTHLY,
        )
        self.account = Account.objects.create(
            user=self.user,
            name="Cuenta principal",
            account_type=Account.ASSET,
            category=Account.SAVINGS_ACCOUNT,
            current_balance=Decimal("5000000.00"),
        )
        self.bill = Bill.objects.create(
            user=self.user,
            provider="Netflix",
            amount=Decimal("45000.00"),
            due_date=timezone.now().date() + timedelta(days=3),
            suggested_account=self.account,
        )
        self.vehicle = Vehicle.objects.create(
            user=self.user, plate="ABC123", brand="Toyota", model="Corolla", year=2020
        )
        self.soat = SOAT.objects.create(
            vehicle=self.vehicle,
            policy_number="SOAT-2025-001",
            issue_date=timezone.now().date(),
            expiry_date=timezone.now().date() + timedelta(days=15),
            cost=80000000,
        )

    def test_list_notifications(self):
        """Test: Listar notificaciones del usuario"""
        # Crear algunas notificaciones
        NotificationEngine.create_budget_warning(
            user=self.user,
            budget=self.budget,
            percentage=85,
            spent=Decimal("850000.00"),
            limit=Decimal("1000000.00"),
        )

        url = "/api/notifications/notifications/"
        response = self.client.get(url)

        assert response.status_code == 200
        # Manejar paginación
        notifications = (
            response.data.get("results", response.data)
            if isinstance(response.data, dict)
            else response.data
        )
        assert isinstance(notifications, list)
        assert len(notifications) > 0

    def test_list_notifications_filter_by_type(self):
        """Test: Filtrar notificaciones por tipo"""
        NotificationEngine.create_budget_warning(
            user=self.user,
            budget=self.budget,
            percentage=85,
            spent=Decimal("850000.00"),
            limit=Decimal("1000000.00"),
        )
        NotificationEngine.create_bill_reminder(
            user=self.user, bill=self.bill, reminder_type="upcoming", days=3
        )

        url = "/api/notifications/notifications/?type=budget_warning"
        response = self.client.get(url)

        assert response.status_code == 200
        notifications = (
            response.data.get("results", response.data)
            if isinstance(response.data, dict)
            else response.data
        )
        for notification in notifications:
            # Verificar que el tipo es budget_warning (puede estar en notification_type o notification_type_display)
            assert (
                notification.get("notification_type") == "budget_warning"
                or "presupuesto" in notification.get("notification_type_display", "").lower()
            )

    def test_list_notifications_filter_by_read(self):
        """Test: Filtrar notificaciones por estado de lectura"""
        notif1 = NotificationEngine.create_budget_warning(
            user=self.user,
            budget=self.budget,
            percentage=85,
            spent=Decimal("850000.00"),
            limit=Decimal("1000000.00"),
        )
        notif1.mark_as_read()

        NotificationEngine.create_budget_exceeded(
            user=self.user,
            budget=self.budget,
            spent=Decimal("1100000.00"),
            limit=Decimal("1000000.00"),
        )

        # Filtrar leídas
        url = "/api/notifications/notifications/?read=true"
        response = self.client.get(url)
        assert response.status_code == 200
        notifications = (
            response.data.get("results", response.data)
            if isinstance(response.data, dict)
            else response.data
        )
        for notification in notifications:
            assert notification["is_read"]

        # Filtrar no leídas
        url = "/api/notifications/notifications/?read=false"
        response = self.client.get(url)
        assert response.status_code == 200
        notifications = (
            response.data.get("results", response.data)
            if isinstance(response.data, dict)
            else response.data
        )
        for notification in notifications:
            assert not notification["is_read"]

    def test_list_notifications_filter_by_dismissed(self):
        """Test: Filtrar notificaciones por estado de descarte"""
        notif1 = NotificationEngine.create_budget_warning(
            user=self.user,
            budget=self.budget,
            percentage=85,
            spent=Decimal("850000.00"),
            limit=Decimal("1000000.00"),
        )
        notif1.mark_as_dismissed()

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
        notifications = (
            response.data.get("results", response.data)
            if isinstance(response.data, dict)
            else response.data
        )
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

    def test_retrieve_notification(self):
        """Test: Obtener detalle de notificación"""
        notification = NotificationEngine.create_budget_warning(
            user=self.user,
            budget=self.budget,
            percentage=85,
            spent=Decimal("850000.00"),
            limit=Decimal("1000000.00"),
        )

        url = f"/api/notifications/notifications/{notification.id}/"
        response = self.client.get(url)

        assert response.status_code == 200
        assert response.data["id"] == notification.id
        # Verificar que tiene información de tipo (puede ser notification_type o notification_type_display)
        assert "notification_type" in response.data or "notification_type_display" in response.data

    def test_mark_as_read_endpoint(self):
        """Test: Marcar notificación como leída"""
        notification = NotificationEngine.create_budget_warning(
            user=self.user,
            budget=self.budget,
            percentage=85,
            spent=Decimal("850000.00"),
            limit=Decimal("1000000.00"),
        )

        url = f"/api/notifications/notifications/{notification.id}/mark_as_read/"
        response = self.client.post(url)

        assert response.status_code == 200
        assert "message" in response.data

        notification.refresh_from_db()
        assert notification.read
        assert notification.read_timestamp is not None

    def test_mark_all_read_endpoint(self):
        """Test: Marcar todas las notificaciones como leídas"""
        NotificationEngine.create_budget_warning(
            user=self.user,
            budget=self.budget,
            percentage=85,
            spent=Decimal("850000.00"),
            limit=Decimal("1000000.00"),
        )
        NotificationEngine.create_budget_exceeded(
            user=self.user,
            budget=self.budget,
            spent=Decimal("1100000.00"),
            limit=Decimal("1000000.00"),
        )

        url = "/api/notifications/notifications/mark_all_read/"
        response = self.client.post(url)

        assert response.status_code == 200
        assert "message" in response.data

        unread_count = Notification.objects.filter(user=self.user, read=False).count()
        assert unread_count == 0

    def test_summary_endpoint(self):
        """Test: Obtener resumen de notificaciones"""
        NotificationEngine.create_budget_warning(
            user=self.user,
            budget=self.budget,
            percentage=85,
            spent=Decimal("850000.00"),
            limit=Decimal("1000000.00"),
        )

        url = "/api/notifications/notifications/summary/"
        response = self.client.get(url)

        assert response.status_code == 200
        assert "total" in response.data
        assert "unread" in response.data
        assert "recent" in response.data
        assert "by_type" in response.data

    def test_custom_reminder_create(self):
        """Test: Crear recordatorio personalizado"""
        url = "/api/notifications/custom-reminders/"
        data = {
            "title": "Reunión importante",
            "message": "No olvidar documentos",
            "reminder_date": (timezone.now().date() + timedelta(days=1)).isoformat(),
            "reminder_time": "09:00:00",
        }

        response = self.client.post(url, data, format="json")

        assert response.status_code == 201
        assert response.data["title"] == "Reunión importante"
        assert not response.data["is_sent"]

    def test_custom_reminder_list(self):
        """Test: Listar recordatorios personalizados"""
        CustomReminder.objects.create(
            user=self.user,
            title="Test reminder",
            message="Test message",
            reminder_date=timezone.now().date() + timedelta(days=1),
            reminder_time=timezone.now().time(),
        )

        url = "/api/notifications/custom-reminders/"
        response = self.client.get(url)

        assert response.status_code == 200
        # Manejar paginación
        reminders = (
            response.data.get("results", response.data)
            if isinstance(response.data, dict)
            else response.data
        )
        assert isinstance(reminders, list)
        assert len(reminders) > 0

    def test_custom_reminder_pending(self):
        """Test: Listar recordatorios pendientes"""
        CustomReminder.objects.create(
            user=self.user,
            title="Pendiente",
            message="Test",
            reminder_date=timezone.now().date() + timedelta(days=1),
            reminder_time=timezone.now().time(),
            is_sent=False,
        )
        CustomReminder.objects.create(
            user=self.user,
            title="Enviado",
            message="Test",
            reminder_date=timezone.now().date() - timedelta(days=1),
            reminder_time=timezone.now().time(),
            is_sent=True,
        )

        url = "/api/notifications/custom-reminders/pending/"
        response = self.client.get(url)

        assert response.status_code == 200
        for reminder in response.data:
            assert not reminder["is_sent"]

    def test_custom_reminder_mark_read(self):
        """Test: Marcar recordatorio como leído"""
        reminder = CustomReminder.objects.create(
            user=self.user,
            title="Test",
            message="Test",
            reminder_date=timezone.now().date() + timedelta(days=1),
            reminder_time=timezone.now().time(),
        )

        url = f"/api/notifications/custom-reminders/{reminder.id}/mark_read/"
        response = self.client.post(url)

        assert response.status_code == 200
        reminder.refresh_from_db()
        assert reminder.is_read

    def test_unauthorized_access(self):
        """Test: Acceso no autorizado sin token"""
        self.client.credentials()

        url = "/api/notifications/notifications/"
        response = self.client.get(url)

        assert response.status_code == 401
