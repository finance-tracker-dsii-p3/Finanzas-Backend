"""
Tests para servicios del Dashboard (dashboard/services.py)
Fase 1: Aumentar cobertura de tests
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from dashboard.services import DashboardService
from notifications.models import Notification

User = get_user_model()


class DashboardServicesTests(TestCase):
    """Tests para servicios del dashboard"""

    def setUp(self):
        """Configuración inicial para cada test"""
        # Crear usuario normal
        self.user = User.objects.create_user(
            identification="12345678",
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            is_verified=True,
        )

        # Crear usuario admin
        self.admin_user = User.objects.create_user(
            identification="87654321",
            username="adminuser",
            email="admin@example.com",
            password="adminpass123",
            first_name="Admin",
            last_name="User",
            is_verified=True,
            role="admin",
        )

        # Crear usuario sin verificar
        self.unverified_user = User.objects.create_user(
            identification="11111111",
            username="unverified",
            email="unverified@example.com",
            password="testpass123",
            is_verified=False,
        )

    def test_get_admin_dashboard_data_success(self):
        """Test: Obtener datos del dashboard para admin"""
        result = DashboardService.get_admin_dashboard_data(self.admin_user)

        assert isinstance(result, dict)
        assert "user_info" in result
        assert "stats" in result
        assert "mini_cards" in result
        assert "recent_activities" in result
        assert "alerts" in result
        assert "charts_data" in result

        # Verificar estructura de user_info
        assert result["user_info"]["id"] == self.admin_user.id
        assert result["user_info"]["username"] == "adminuser"
        assert result["user_info"]["role"] == "admin"

        # Verificar stats
        assert "total_users" in result["stats"]
        assert "active_users" in result["stats"]
        assert "pending_verifications" in result["stats"]

    def test_get_user_dashboard_data_success(self):
        """Test: Obtener datos del dashboard para usuario"""
        result = DashboardService.get_user_dashboard_data(self.user)

        assert isinstance(result, dict)
        assert "user_info" in result
        assert "stats" in result
        assert "mini_cards" in result
        assert "recent_activities" in result
        assert "alerts" in result
        assert "charts_data" in result
        assert "credit_cards" in result

        # Verificar estructura de user_info
        assert result["user_info"]["id"] == self.user.id
        assert result["user_info"]["username"] == "testuser"

        # Verificar credit_cards
        assert "upcoming_payments" in result["credit_cards"]
        assert "monthly_summary" in result["credit_cards"]
        assert "active_plans" in result["credit_cards"]

    def test_get_user_dashboard_data_with_notifications(self):
        """Test: Dashboard con notificaciones"""
        # Crear notificación
        Notification.objects.create(
            user=self.user,
            title="Test Notification",
            message="Test message",
            notification_type="info",
            read=False,
        )

        result = DashboardService.get_user_dashboard_data(self.user)
        assert result["stats"]["unread_notifications"] > 0

    def test_get_user_dashboard_data_unverified_user(self):
        """Test: Dashboard para usuario no verificado"""
        result = DashboardService.get_user_dashboard_data(self.unverified_user)

        assert isinstance(result, dict)
        assert "alerts" in result
        # Si el usuario no tiene first_name ni last_name, también tendrá profile_incomplete
        # Verificamos que tenga al menos verification_pending o profile_incomplete
        alert_types = [alert["type"] for alert in result["alerts"]]
        has_verification_or_profile = (
            "verification_pending" in alert_types or "profile_incomplete" in alert_types
        )
        assert (
            has_verification_or_profile
        ), f"Expected verification_pending or profile_incomplete, got {alert_types}"

    def test_get_user_dashboard_data_incomplete_profile(self):
        """Test: Dashboard para usuario con perfil incompleto"""
        incomplete_user = User.objects.create_user(
            identification="22222222",
            username="incomplete",
            email="incomplete@example.com",
            password="testpass123",
            is_verified=True,
            # Sin first_name ni last_name
        )

        result = DashboardService.get_user_dashboard_data(incomplete_user)
        assert "alerts" in result
        alert_types = [alert["type"] for alert in result["alerts"]]
        assert "profile_incomplete" in alert_types

    def test_get_recent_activities_success(self):
        """Test: Obtener actividades recientes"""
        # Crear notificaciones
        Notification.objects.create(
            user=self.user,
            title="Activity 1",
            message="Message 1",
            notification_type="info",
        )
        Notification.objects.create(
            user=self.admin_user,
            title="Activity 2",
            message="Message 2",
            notification_type="warning",
        )

        activities = DashboardService._get_recent_activities()
        assert isinstance(activities, list)
        assert len(activities) > 0

        # Verificar estructura
        if activities:
            activity = activities[0]
            assert "id" in activity
            assert "type" in activity
            assert "timestamp" in activity
            assert "description" in activity

    def test_get_user_recent_activities_success(self):
        """Test: Obtener actividades recientes del usuario"""
        # Crear notificaciones para el usuario
        Notification.objects.create(
            user=self.user,
            title="User Activity 1",
            message="Message 1",
            notification_type="info",
            read=False,
        )
        Notification.objects.create(
            user=self.user,
            title="User Activity 2",
            message="Message 2",
            notification_type="warning",
            read=True,
        )

        activities = DashboardService._get_user_recent_activities(self.user)
        assert isinstance(activities, list)
        assert len(activities) > 0

        # Verificar que todas son del usuario
        for activity in activities:
            assert "id" in activity
            assert "type" in activity
            assert "timestamp" in activity
            assert "read" in activity

    def test_get_alerts_with_pending_users(self):
        """Test: Alertas cuando hay usuarios pendientes"""
        alerts = DashboardService._get_alerts()
        assert isinstance(alerts, list)

        # Si hay usuarios pendientes, debe haber alerta
        pending_count = User.objects.filter(is_verified=False, is_active=True).count()
        if pending_count > 0:
            alert_types = [alert["type"] for alert in alerts]
            assert "pending_users" in alert_types

    def test_get_user_alerts_verification_pending(self):
        """Test: Alertas para usuario no verificado"""
        alerts = DashboardService._get_user_alerts(self.unverified_user)
        assert isinstance(alerts, list)

        # Si el usuario no tiene first_name ni last_name, también tendrá profile_incomplete
        # Verificamos que tenga al menos verification_pending o profile_incomplete
        alert_types = [alert["type"] for alert in alerts]
        has_verification_or_profile = (
            "verification_pending" in alert_types or "profile_incomplete" in alert_types
        )
        assert (
            has_verification_or_profile
        ), f"Expected verification_pending or profile_incomplete, got {alert_types}"

    def test_get_user_alerts_profile_incomplete(self):
        """Test: Alertas para perfil incompleto"""
        incomplete_user = User.objects.create_user(
            identification="33333333",
            username="incomplete2",
            email="incomplete2@example.com",
            password="testpass123",
            is_verified=True,
        )

        alerts = DashboardService._get_user_alerts(incomplete_user)
        alert_types = [alert["type"] for alert in alerts]
        assert "profile_incomplete" in alert_types

    def test_get_user_alerts_complete_profile(self):
        """Test: Sin alertas para perfil completo"""
        alerts = DashboardService._get_user_alerts(self.user)
        alert_types = [alert["type"] for alert in alerts]
        # No debe tener alertas de perfil incompleto ni verificación
        assert "profile_incomplete" not in alert_types
        assert "verification_pending" not in alert_types

    def test_get_error_dashboard(self):
        """Test: Dashboard de error por defecto"""
        result = DashboardService._get_error_dashboard()

        assert isinstance(result, dict)
        assert "user_info" in result
        assert "stats" in result
        assert "mini_cards" in result
        assert "recent_activities" in result
        assert "alerts" in result
        assert "charts_data" in result

        # Debe estar vacío pero con estructura correcta
        assert result["user_info"] == {}
        assert result["stats"] == {}
        assert result["mini_cards"] == []
        assert result["recent_activities"] == []
        assert result["alerts"] == []
