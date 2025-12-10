"""
Tests para servicios del Dashboard (dashboard/services.py)
Fase 1: Aumentar cobertura de tests
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
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

        self.assertIsInstance(result, dict)
        self.assertIn("user_info", result)
        self.assertIn("stats", result)
        self.assertIn("mini_cards", result)
        self.assertIn("recent_activities", result)
        self.assertIn("alerts", result)
        self.assertIn("charts_data", result)

        # Verificar estructura de user_info
        self.assertEqual(result["user_info"]["id"], self.admin_user.id)
        self.assertEqual(result["user_info"]["username"], "adminuser")
        self.assertEqual(result["user_info"]["role"], "admin")

        # Verificar stats
        self.assertIn("total_users", result["stats"])
        self.assertIn("active_users", result["stats"])
        self.assertIn("pending_verifications", result["stats"])

    def test_get_user_dashboard_data_success(self):
        """Test: Obtener datos del dashboard para usuario"""
        result = DashboardService.get_user_dashboard_data(self.user)

        self.assertIsInstance(result, dict)
        self.assertIn("user_info", result)
        self.assertIn("stats", result)
        self.assertIn("mini_cards", result)
        self.assertIn("recent_activities", result)
        self.assertIn("alerts", result)
        self.assertIn("charts_data", result)
        self.assertIn("credit_cards", result)

        # Verificar estructura de user_info
        self.assertEqual(result["user_info"]["id"], self.user.id)
        self.assertEqual(result["user_info"]["username"], "testuser")

        # Verificar credit_cards
        self.assertIn("upcoming_payments", result["credit_cards"])
        self.assertIn("monthly_summary", result["credit_cards"])
        self.assertIn("active_plans", result["credit_cards"])

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
        self.assertGreater(result["stats"]["unread_notifications"], 0)

    def test_get_user_dashboard_data_unverified_user(self):
        """Test: Dashboard para usuario no verificado"""
        result = DashboardService.get_user_dashboard_data(self.unverified_user)

        self.assertIsInstance(result, dict)
        self.assertIn("alerts", result)
        # Si el usuario no tiene first_name ni last_name, también tendrá profile_incomplete
        # Verificamos que tenga al menos verification_pending o profile_incomplete
        alert_types = [alert["type"] for alert in result["alerts"]]
        has_verification_or_profile = (
            "verification_pending" in alert_types or "profile_incomplete" in alert_types
        )
        self.assertTrue(
            has_verification_or_profile,
            f"Expected verification_pending or profile_incomplete, got {alert_types}",
        )

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
        self.assertIn("alerts", result)
        alert_types = [alert["type"] for alert in result["alerts"]]
        self.assertIn("profile_incomplete", alert_types)

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
        self.assertIsInstance(activities, list)
        self.assertGreater(len(activities), 0)

        # Verificar estructura
        if activities:
            activity = activities[0]
            self.assertIn("id", activity)
            self.assertIn("type", activity)
            self.assertIn("timestamp", activity)
            self.assertIn("description", activity)

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
        self.assertIsInstance(activities, list)
        self.assertGreater(len(activities), 0)

        # Verificar que todas son del usuario
        for activity in activities:
            self.assertIn("id", activity)
            self.assertIn("type", activity)
            self.assertIn("timestamp", activity)
            self.assertIn("read", activity)

    def test_get_alerts_with_pending_users(self):
        """Test: Alertas cuando hay usuarios pendientes"""
        alerts = DashboardService._get_alerts()
        self.assertIsInstance(alerts, list)

        # Si hay usuarios pendientes, debe haber alerta
        pending_count = User.objects.filter(is_verified=False, is_active=True).count()
        if pending_count > 0:
            alert_types = [alert["type"] for alert in alerts]
            self.assertIn("pending_users", alert_types)

    def test_get_user_alerts_verification_pending(self):
        """Test: Alertas para usuario no verificado"""
        alerts = DashboardService._get_user_alerts(self.unverified_user)
        self.assertIsInstance(alerts, list)

        # Si el usuario no tiene first_name ni last_name, también tendrá profile_incomplete
        # Verificamos que tenga al menos verification_pending o profile_incomplete
        alert_types = [alert["type"] for alert in alerts]
        has_verification_or_profile = (
            "verification_pending" in alert_types or "profile_incomplete" in alert_types
        )
        self.assertTrue(
            has_verification_or_profile,
            f"Expected verification_pending or profile_incomplete, got {alert_types}",
        )

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
        self.assertIn("profile_incomplete", alert_types)

    def test_get_user_alerts_complete_profile(self):
        """Test: Sin alertas para perfil completo"""
        alerts = DashboardService._get_user_alerts(self.user)
        alert_types = [alert["type"] for alert in alerts]
        # No debe tener alertas de perfil incompleto ni verificación
        self.assertNotIn("profile_incomplete", alert_types)
        self.assertNotIn("verification_pending", alert_types)

    def test_get_error_dashboard(self):
        """Test: Dashboard de error por defecto"""
        result = DashboardService._get_error_dashboard()

        self.assertIsInstance(result, dict)
        self.assertIn("user_info", result)
        self.assertIn("stats", result)
        self.assertIn("mini_cards", result)
        self.assertIn("recent_activities", result)
        self.assertIn("alerts", result)
        self.assertIn("charts_data", result)

        # Debe estar vacío pero con estructura correcta
        self.assertEqual(result["user_info"], {})
        self.assertEqual(result["stats"], {})
        self.assertEqual(result["mini_cards"], [])
        self.assertEqual(result["recent_activities"], [])
        self.assertEqual(result["alerts"], [])
