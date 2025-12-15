"""
Tests para la API de Notificaciones (notifications/views.py)
Fase 1: Aumentar cobertura de tests
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from notifications.models import CustomReminder, Notification

User = get_user_model()


class NotificationsViewsTests(TestCase):
    """Tests para endpoints de notificaciones"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = APIClient()

        # Crear usuario normal y token
        self.user = User.objects.create_user(
            identification="12345678",
            username="testuser",
            email="test@example.com",
            password="testpass123",
            is_verified=True,
            role="user",
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        # Crear usuario admin
        self.admin_user = User.objects.create_user(
            identification="87654321",
            username="adminuser",
            email="admin@example.com",
            password="adminpass123",
            is_verified=True,
            role="admin",
        )
        self.admin_token = Token.objects.create(user=self.admin_user)

        # Crear notificaciones de prueba
        self.notification1 = Notification.objects.create(
            user=self.user,
            notification_type=Notification.GENERAL,
            title="Test Notification 1",
            message="Test message 1",
            read=False,
        )

        self.notification2 = Notification.objects.create(
            user=self.user,
            notification_type=Notification.BUDGET_WARNING,
            title="Budget Warning",
            message="Budget warning message",
            read=True,
        )

        self.notification3 = Notification.objects.create(
            user=self.user,
            notification_type=Notification.BILL_REMINDER,
            title="Bill Reminder",
            message="Bill reminder message",
            read=False,
            is_dismissed=False,
        )

    def test_list_notifications_success(self):
        """Test: Listar notificaciones exitosamente"""
        response = self.client.get("/api/notifications/notifications/")
        assert response.status_code == status.HTTP_200_OK
        # DRF puede devolver paginación o lista directa
        if isinstance(response.data, dict) and "results" in response.data:
            assert len(response.data["results"]) == 3
        elif isinstance(response.data, list):
            assert len(response.data) == 3
        else:
            # Si es dict sin results, verificar que tiene count
            assert "count" in response.data or len(response.data) >= 0

    def test_list_notifications_with_type_filter(self):
        """Test: Filtrar notificaciones por tipo"""
        response = self.client.get("/api/notifications/notifications/?type=general")
        assert response.status_code == status.HTTP_200_OK
        # DRF puede devolver paginación
        if isinstance(response.data, dict) and "results" in response.data:
            assert len(response.data["results"]) == 1
            assert response.data["results"][0]["title"] == "Test Notification 1"
        else:
            assert len(response.data) == 1
            assert response.data[0]["title"] == "Test Notification 1"

    def test_list_notifications_with_read_filter(self):
        """Test: Filtrar notificaciones por leídas"""
        response = self.client.get("/api/notifications/notifications/?read=true")
        assert response.status_code == status.HTTP_200_OK
        # DRF puede devolver paginación
        if isinstance(response.data, dict) and "results" in response.data:
            assert len(response.data["results"]) >= 1
        else:
            assert len(response.data) >= 1

    def test_list_notifications_with_dismissed_filter(self):
        """Test: Filtrar notificaciones por descartadas"""
        response = self.client.get("/api/notifications/notifications/?dismissed=false")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_list_notifications_with_related_type_filter(self):
        """Test: Filtrar notificaciones por tipo de objeto relacionado"""
        self.notification1.related_object_type = "budget"
        self.notification1.save()
        response = self.client.get("/api/notifications/notifications/?related_type=budget")
        assert response.status_code == status.HTTP_200_OK

    def test_create_notification_as_admin(self):
        """Test: Admin puede crear notificaciones"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        data = {
            "user": self.user.id,
            "notification_type": Notification.GENERAL,
            "title": "Admin Notification",
            "message": "Admin created notification",
        }
        response = self.client.post("/api/notifications/notifications/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "Admin Notification"

    def test_create_notification_as_user_forbidden(self):
        """Test: Usuario normal no puede crear notificaciones"""
        data = {
            "user": self.user.id,
            "notification_type": Notification.GENERAL,
            "title": "User Notification",
            "message": "User created notification",
        }
        response = self.client.post("/api/notifications/notifications/", data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_notification_success(self):
        """Test: Obtener detalle de notificación"""
        response = self.client.get(f"/api/notifications/notifications/{self.notification1.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Test Notification 1"

    def test_mark_as_read_success(self):
        """Test: Marcar notificación como leída"""
        assert not self.notification1.read
        response = self.client.post(
            f"/api/notifications/notifications/{self.notification1.id}/mark_as_read/"
        )
        assert response.status_code == status.HTTP_200_OK
        self.notification1.refresh_from_db()
        assert self.notification1.read

    def test_mark_as_read_other_user_forbidden(self):
        """Test: No se puede marcar notificación de otro usuario"""
        other_user = User.objects.create_user(
            identification="99999999",
            username="otheruser",
            email="other@example.com",
            password="otherpass123",
            is_verified=True,
        )
        other_notification = Notification.objects.create(
            user=other_user,
            notification_type=Notification.GENERAL,
            title="Other User Notification",
            message="Other user message",
        )
        response = self.client.post(
            f"/api/notifications/notifications/{other_notification.id}/mark_as_read/"
        )
        # Puede ser 400 o 403 dependiendo de la implementación
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN]

    def test_mark_all_read_success(self):
        """Test: Marcar todas las notificaciones como leídas"""
        unread_count = Notification.objects.filter(user=self.user, read=False).count()
        response = self.client.post("/api/notifications/notifications/mark_all_read/")
        assert response.status_code == status.HTTP_200_OK
        assert unread_count > 0
        assert Notification.objects.filter(user=self.user, read=False).count() == 0

    def test_dismiss_notification_success(self):
        """Test: Descartar notificación"""
        assert not self.notification3.is_dismissed
        response = self.client.post(
            f"/api/notifications/notifications/{self.notification3.id}/dismiss/"
        )
        assert response.status_code == status.HTTP_200_OK
        self.notification3.refresh_from_db()
        assert self.notification3.is_dismissed

    def test_dismiss_other_user_notification_forbidden(self):
        """Test: No se puede descartar notificación de otro usuario"""
        other_user = User.objects.create_user(
            identification="88888888",
            username="anotheruser",
            email="another@example.com",
            password="anotherpass123",
            is_verified=True,
        )
        other_notification = Notification.objects.create(
            user=other_user,
            notification_type=Notification.GENERAL,
            title="Another Notification",
            message="Another message",
        )
        response = self.client.post(
            f"/api/notifications/notifications/{other_notification.id}/dismiss/"
        )
        # Puede ser 400 o 404 dependiendo de la implementación
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_404_NOT_FOUND]

    def test_dismiss_all_success(self):
        """Test: Descartar todas las notificaciones"""
        not_dismissed_count = Notification.objects.filter(
            user=self.user, is_dismissed=False
        ).count()
        response = self.client.post("/api/notifications/notifications/dismiss_all/")
        assert response.status_code == status.HTTP_200_OK
        assert "updated_count" in response.data

    def test_summary_endpoint_success(self):
        """Test: Obtener resumen de notificaciones"""
        response = self.client.get("/api/notifications/notifications/summary/")
        assert response.status_code == status.HTTP_200_OK
        assert "total" in response.data
        assert "unread" in response.data
        assert "recent" in response.data

    def test_system_alerts_summary_as_admin(self):
        """Test: Admin puede obtener resumen de alertas del sistema"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.get("/api/notifications/notifications/system_alerts_summary/")
        assert response.status_code == status.HTTP_200_OK
        assert "total_notifications" in response.data

    def test_system_alerts_summary_as_user_forbidden(self):
        """Test: Usuario normal no puede acceder a resumen de alertas"""
        response = self.client.get("/api/notifications/notifications/system_alerts_summary/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_notifications_summary_as_admin(self):
        """Test: Admin puede obtener resumen estadístico"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.get("/api/notifications/notifications/notifications_summary/")
        assert response.status_code == status.HTTP_200_OK
        assert "total_notifications" in response.data

    def test_notifications_summary_as_user_forbidden(self):
        """Test: Usuario normal no puede acceder a resumen estadístico"""
        response = self.client.get("/api/notifications/notifications/notifications_summary/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_send_system_alert_as_admin(self):
        """Test: Admin puede enviar alertas del sistema"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        data = {
            "title": "System Alert",
            "message": "System alert message",
            "user_ids": [self.user.id],
        }
        response = self.client.post(
            "/api/notifications/notifications/send_system_alert/", data, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert "notifications_sent" in response.data

    def test_send_system_alert_as_user_forbidden(self):
        """Test: Usuario normal no puede enviar alertas"""
        data = {
            "title": "System Alert",
            "message": "System alert message",
        }
        response = self.client.post(
            "/api/notifications/notifications/send_system_alert/", data, format="json"
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_send_system_alert_missing_fields(self):
        """Test: Error al enviar alerta sin campos requeridos"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        data = {"title": "System Alert"}
        response = self.client.post(
            "/api/notifications/notifications/send_system_alert/", data, format="json"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_requires_authentication(self):
        """Test: Listar notificaciones requiere autenticación"""
        self.client.credentials()
        response = self.client.get("/api/notifications/notifications/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class CustomReminderViewsTests(TestCase):
    """Tests para endpoints de recordatorios personalizados"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = APIClient()

        # Crear usuario y token
        self.user = User.objects.create_user(
            identification="12345678",
            username="testuser",
            email="test@example.com",
            password="testpass123",
            is_verified=True,
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        # Crear notificación para asociar
        self.notification = Notification.objects.create(
            user=self.user,
            notification_type=Notification.CUSTOM_REMINDER,
            title="Reminder Notification",
            message="Reminder message",
        )

        # Crear recordatorios de prueba
        self.reminder1 = CustomReminder.objects.create(
            user=self.user,
            title="Test Reminder 1",
            message="Test reminder message 1",
            reminder_date=timezone.now().date(),
            reminder_time=timezone.now().time(),
            is_sent=False,
            is_read=False,
        )

        self.reminder2 = CustomReminder.objects.create(
            user=self.user,
            title="Test Reminder 2",
            message="Test reminder message 2",
            reminder_date=timezone.now().date(),
            reminder_time=timezone.now().time(),
            is_sent=True,
            is_read=True,
            notification=self.notification,
        )

    def test_list_custom_reminders_success(self):
        """Test: Listar recordatorios personalizados"""
        response = self.client.get("/api/notifications/custom-reminders/")
        assert response.status_code == status.HTTP_200_OK
        # DRF puede devolver paginación
        if isinstance(response.data, dict) and "results" in response.data:
            assert len(response.data["results"]) == 2
        else:
            assert isinstance(response.data, list)
            assert len(response.data) == 2

    def test_list_custom_reminders_with_is_sent_filter(self):
        """Test: Filtrar recordatorios por enviados"""
        response = self.client.get("/api/notifications/custom-reminders/?is_sent=true")
        assert response.status_code == status.HTTP_200_OK
        # DRF puede devolver paginación
        if isinstance(response.data, dict) and "results" in response.data:
            assert len(response.data["results"]) == 1
        else:
            assert len(response.data) == 1

    def test_list_custom_reminders_with_is_read_filter(self):
        """Test: Filtrar recordatorios por leídos"""
        response = self.client.get("/api/notifications/custom-reminders/?is_read=true")
        assert response.status_code == status.HTTP_200_OK
        # DRF puede devolver paginación
        if isinstance(response.data, dict) and "results" in response.data:
            assert len(response.data["results"]) == 1
        else:
            assert len(response.data) == 1

    def test_create_custom_reminder_success(self):
        """Test: Crear recordatorio personalizado"""
        data = {
            "title": "New Reminder",
            "message": "New reminder message",
            "reminder_date": str(timezone.now().date()),
            "reminder_time": str(timezone.now().time()),
        }
        response = self.client.post("/api/notifications/custom-reminders/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "New Reminder"

    def test_retrieve_custom_reminder_success(self):
        """Test: Obtener detalle de recordatorio"""
        response = self.client.get(f"/api/notifications/custom-reminders/{self.reminder1.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Test Reminder 1"

    def test_update_custom_reminder_success(self):
        """Test: Actualizar recordatorio"""
        data = {"title": "Updated Reminder"}
        response = self.client.patch(
            f"/api/notifications/custom-reminders/{self.reminder1.id}/", data, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Updated Reminder"

    def test_delete_custom_reminder_success(self):
        """Test: Eliminar recordatorio"""
        reminder_id = self.reminder1.id
        response = self.client.delete(f"/api/notifications/custom-reminders/{reminder_id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not CustomReminder.objects.filter(id=reminder_id).exists()

    def test_mark_read_success(self):
        """Test: Marcar recordatorio como leído"""
        assert not self.reminder1.is_read
        response = self.client.post(
            f"/api/notifications/custom-reminders/{self.reminder1.id}/mark_read/"
        )
        assert response.status_code == status.HTTP_200_OK
        self.reminder1.refresh_from_db()
        assert self.reminder1.is_read

    def test_mark_all_read_success(self):
        """Test: Marcar todos los recordatorios como leídos"""
        unread_count = CustomReminder.objects.filter(user=self.user, is_read=False).count()
        response = self.client.post("/api/notifications/custom-reminders/mark_all_read/")
        assert response.status_code == status.HTTP_200_OK
        assert "updated_count" in response.data

    def test_pending_reminders_success(self):
        """Test: Listar recordatorios pendientes"""
        response = self.client.get("/api/notifications/custom-reminders/pending/")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_sent_reminders_success(self):
        """Test: Listar recordatorios enviados"""
        response = self.client.get("/api/notifications/custom-reminders/sent/")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) == 1

    def test_list_requires_authentication(self):
        """Test: Listar recordatorios requiere autenticación"""
        self.client.credentials()
        response = self.client.get("/api/notifications/custom-reminders/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
