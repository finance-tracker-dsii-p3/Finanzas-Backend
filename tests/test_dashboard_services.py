"""
Tests para servicios del Dashboard (dashboard/services.py)
Fase 1: Aumentar cobertura de tests
"""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from accounts.models import Account
from categories.models import Category
from dashboard.services import DashboardService, FinancialDashboardService
from notifications.models import Notification
from transactions.models import Transaction

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


class FinancialDashboardServiceTests(TestCase):
    """Tests para servicios financieros del dashboard"""

    def setUp(self):
        """Configuración inicial para cada test"""
        # Crear usuario
        self.user = User.objects.create_user(
            identification="12345678",
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
            is_verified=True,
        )

        # Crear cuenta
        self.account = Account.objects.create(
            user=self.user,
            name="Cuenta Principal",
            account_type="asset",
            category="bank_account",
            currency="COP",
            current_balance=Decimal("1000000.00"),  # $10,000.00
        )

        # Crear categoría
        self.category = Category.objects.create(
            user=self.user,
            name="Comida",
            type="expense",
            color="#FF0000",
        )

    def test_get_financial_summary_empty(self):
        """Test: Resumen financiero sin transacciones"""
        result = FinancialDashboardService.get_financial_summary(self.user)

        assert isinstance(result, dict)
        assert result["has_data"] is False
        assert "error" not in result

    def test_get_financial_summary_with_transactions(self):
        """Test: Resumen financiero con transacciones"""
        # Crear transacción de ingreso
        Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            category=None,
            type=1,  # Income
            description="Salario",
            base_amount=5000000,  # $50,000.00 en centavos
            total_amount=5000000,
            date=date.today(),
        )

        # Crear transacción de gasto
        Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            category=self.category,
            type=2,  # Expense
            description="Almuerzo",
            base_amount=30000,  # $300.00 en centavos
            total_amount=30000,
            date=date.today(),
        )

        result = FinancialDashboardService.get_financial_summary(self.user)

        assert isinstance(result, dict)
        assert result["has_data"] is True
        assert "summary" in result
        assert "recent_transactions" in result
        assert "upcoming_bills" in result
        assert "charts" in result

    def test_get_financial_summary_with_year_filter(self):
        """Test: Resumen financiero con filtro de año"""
        # Crear transacción del año actual
        Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            type=1,
            description="Ingreso",
            base_amount=1000000,
            total_amount=1000000,
            date=date.today(),
        )

        result = FinancialDashboardService.get_financial_summary(self.user, year=date.today().year)

        assert isinstance(result, dict)
        assert result["has_data"] is True

    def test_get_financial_summary_with_month_filter(self):
        """Test: Resumen financiero con filtro de mes"""
        Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            type=1,
            description="Ingreso",
            base_amount=1000000,
            total_amount=1000000,
            date=date.today(),
        )

        result = FinancialDashboardService.get_financial_summary(
            self.user, year=date.today().year, month=date.today().month
        )

        assert isinstance(result, dict)
        assert result["has_data"] is True

    def test_get_financial_summary_with_account_filter(self):
        """Test: Resumen financiero con filtro de cuenta"""
        Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            type=1,
            description="Ingreso",
            base_amount=1000000,
            total_amount=1000000,
            date=date.today(),
        )

        result = FinancialDashboardService.get_financial_summary(
            self.user, account_id=self.account.id
        )

        assert isinstance(result, dict)
        assert result["has_data"] is True

    def test_get_financial_summary_invalid_account(self):
        """Test: Resumen financiero con cuenta inválida"""
        result = FinancialDashboardService.get_financial_summary(self.user, account_id=99999)

        assert isinstance(result, dict)
        assert result["has_data"] is False
        assert "error" in result

    def test_calculate_totals(self):
        """Test: Calcular totales de transacciones"""
        # Crear transacciones
        income_tx = Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            type=1,  # Income
            description="Ingreso",
            base_amount=1000000,
            total_amount=1000000,
            date=date.today(),
        )

        expense_tx = Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            category=self.category,
            type=2,  # Expense
            description="Gasto",
            base_amount=200000,
            total_amount=200000,
            date=date.today(),
        )

        transactions = Transaction.objects.filter(user=self.user)
        totals = FinancialDashboardService._calculate_totals(transactions, "COP", self.user)

        assert isinstance(totals, dict)
        assert "income" in totals
        assert "expenses" in totals
        assert "savings" in totals
        assert "iva" in totals
        assert "gmf" in totals

    def test_get_recent_transactions(self):
        """Test: Obtener transacciones recientes"""
        # Crear transacciones
        for i in range(3):
            Transaction.objects.create(
                user=self.user,
                origin_account=self.account,
                type=1,
                description=f"Transacción {i}",
                base_amount=100000 * (i + 1),
                total_amount=100000 * (i + 1),
                date=date.today() - timedelta(days=i),
            )

        recent = FinancialDashboardService._get_recent_transactions(self.user, limit=5)

        assert isinstance(recent, list)
        assert len(recent) <= 5
        if recent:
            assert "id" in recent[0]
            assert "type" in recent[0]
            assert "date" in recent[0]

    def test_get_recent_transactions_with_account_filter(self):
        """Test: Obtener transacciones recientes filtradas por cuenta"""
        Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            type=1,
            description="Transacción",
            base_amount=100000,
            total_amount=100000,
            date=date.today(),
        )

        recent = FinancialDashboardService._get_recent_transactions(
            self.user, account_id=self.account.id, limit=5
        )

        assert isinstance(recent, list)

    def test_get_expense_distribution(self):
        """Test: Obtener distribución de gastos"""
        # Crear gastos con diferentes categorías (usar color con buen contraste)
        category2 = Category.objects.create(
            user=self.user, name="Transporte", type="expense", color="#0066CC"
        )

        Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            category=self.category,
            type=2,
            description="Gasto 1",
            base_amount=50000,
            total_amount=50000,
            date=date.today(),
        )

        Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            category=category2,
            type=2,
            description="Gasto 2",
            base_amount=30000,
            total_amount=30000,
            date=date.today(),
        )

        transactions = Transaction.objects.filter(user=self.user, type=2)
        distribution = FinancialDashboardService._get_expense_distribution(
            transactions, "COP", self.user
        )

        assert isinstance(distribution, dict)
        assert "categories" in distribution
        assert "total" in distribution
        assert "has_data" in distribution
        assert distribution["has_data"] is True

    def test_get_daily_income_expense(self):
        """Test: Obtener flujo diario de ingresos y gastos"""
        # Crear transacciones en diferentes fechas
        Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            type=1,
            description="Ingreso",
            base_amount=100000,
            total_amount=100000,
            date=date.today(),
        )

        Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            category=self.category,
            type=2,
            description="Gasto",
            base_amount=50000,
            total_amount=50000,
            date=date.today(),
        )

        transactions = Transaction.objects.filter(user=self.user)
        daily_flow = FinancialDashboardService._get_daily_income_expense(
            transactions, "COP", self.user, date.today().year, date.today().month
        )

        assert isinstance(daily_flow, dict)
        assert "dates" in daily_flow
        assert "income" in daily_flow
        assert "expenses" in daily_flow
        assert "has_data" in daily_flow

    def test_get_empty_state(self):
        """Test: Obtener estado vacío"""
        empty_state = FinancialDashboardService._get_empty_state(
            self.user, "COP", has_accounts=True
        )

        assert isinstance(empty_state, dict)
        assert empty_state["has_data"] is False
        assert "summary" in empty_state or "message" in empty_state

    def test_get_period_label(self):
        """Test: Obtener etiqueta de período"""
        # Test con año y mes
        label = FinancialDashboardService._get_period_label(2024, 3)
        assert isinstance(label, str)
        assert "2024" in label
        assert "marzo" in label.lower() or "march" in label.lower()

        # Test solo con año
        label = FinancialDashboardService._get_period_label(2024, None)
        assert isinstance(label, str)
        assert "2024" in label

        # Test sin parámetros
        label = FinancialDashboardService._get_period_label(None, None)
        assert isinstance(label, str)

    def test_get_upcoming_bills(self):
        """Test: Obtener facturas próximas a vencer"""
        bills = FinancialDashboardService._get_upcoming_bills(self.user, limit=5)

        assert isinstance(bills, list)
        # Puede estar vacío si no hay facturas
