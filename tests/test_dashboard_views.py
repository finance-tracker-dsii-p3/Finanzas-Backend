"""
Tests para dashboard/views.py para aumentar coverage
"""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from rest_framework.authtoken.models import Token

User = get_user_model()


class DashboardViewsTests(TestCase):
    """Tests para views del dashboard"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = Client()

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

        # Crear tokens
        self.user_token = Token.objects.create(user=self.user)
        self.admin_token = Token.objects.create(user=self.admin_user)

        # Headers para autenticación
        self.user_headers = {
            "HTTP_AUTHORIZATION": f"Token {self.user_token.key}",
        }

        self.admin_headers = {
            "HTTP_AUTHORIZATION": f"Token {self.admin_token.key}",
        }

    def test_dashboard_view_user(self):
        """Test: Vista principal del dashboard para usuario"""
        response = self.client.get("/api/dashboard/", **self.user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "data" in data

    def test_dashboard_view_admin(self):
        """Test: Vista principal del dashboard para admin"""
        response = self.client.get("/api/dashboard/", **self.admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data

    def test_mini_cards_view(self):
        """Test: Vista de mini cards"""
        response = self.client.get("/api/dashboard/mini-cards/", **self.user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "mini_cards" in data

    def test_stats_view(self):
        """Test: Vista de estadísticas"""
        response = self.client.get("/api/dashboard/stats/", **self.user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "stats" in data

    def test_alerts_view(self):
        """Test: Vista de alertas"""
        response = self.client.get("/api/dashboard/alerts/", **self.user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "alerts" in data

    def test_charts_data_view(self):
        """Test: Vista de datos de gráficos"""
        response = self.client.get("/api/dashboard/charts/", **self.user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "charts_data" in data

    def test_admin_overview_view(self):
        """Test: Vista de resumen administrativo"""
        response = self.client.get("/api/dashboard/admin/overview/", **self.admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "overview" in data

    def test_admin_overview_view_requires_admin(self):
        """Test: Vista de resumen requiere admin"""
        response = self.client.get("/api/dashboard/admin/overview/", **self.user_headers)
        assert response.status_code == 403

    def test_financial_dashboard_view(self):
        """Test: Vista de dashboard financiero"""
        response = self.client.get("/api/dashboard/financial/", **self.user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "data" in data

    def test_financial_dashboard_view_with_year(self):
        """Test: Dashboard financiero con filtro de año"""
        response = self.client.get("/api/dashboard/financial/?year=2025", **self.user_headers)
        assert response.status_code == 200

    def test_financial_dashboard_view_with_month(self):
        """Test: Dashboard financiero con filtro de mes"""
        response = self.client.get(
            "/api/dashboard/financial/?year=2025&month=12", **self.user_headers
        )
        assert response.status_code == 200

    def test_financial_dashboard_view_invalid_year(self):
        """Test: Dashboard financiero con año inválido"""
        response = self.client.get("/api/dashboard/financial/?year=1999", **self.user_headers)
        assert response.status_code == 400

    def test_financial_dashboard_view_invalid_month(self):
        """Test: Dashboard financiero con mes inválido"""
        response = self.client.get(
            "/api/dashboard/financial/?year=2025&month=13", **self.user_headers
        )
        assert response.status_code == 400

    def test_financial_dashboard_view_month_without_year(self):
        """Test: Dashboard financiero con mes sin año"""
        response = self.client.get("/api/dashboard/financial/?month=12", **self.user_headers)
        assert response.status_code == 400

    def test_financial_dashboard_view_with_all(self):
        """Test: Dashboard financiero con all=true"""
        response = self.client.get("/api/dashboard/financial/?all=true", **self.user_headers)
        assert response.status_code == 200
