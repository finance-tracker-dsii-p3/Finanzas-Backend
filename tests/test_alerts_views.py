"""
Tests para la API de Alertas (alerts/views.py)
Fase 1: Aumentar cobertura de tests
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from alerts.models import Alert
from budgets.models import Budget
from categories.models import Category

User = get_user_model()


class AlertsViewsTests(TestCase):
    """Tests para endpoints de alertas"""

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

        # Crear categoría y presupuesto para las alertas
        self.category = Category.objects.create(
            user=self.user,
            name="Comida",
            type=Category.EXPENSE,
            color="#DC2626",
            icon="fa-utensils",
        )

        self.budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=100000.00,
            currency="COP",
            calculation_mode=Budget.BASE,
            period=Budget.MONTHLY,
            is_active=True,
        )

        # Crear alertas de prueba
        self.alert1 = Alert.objects.create(
            user=self.user,
            budget=self.budget,
            alert_type="warning",
            is_read=False,
        )

        self.alert2 = Alert.objects.create(
            user=self.user,
            budget=self.budget,
            alert_type="exceeded",
            is_read=True,
        )

    def test_list_alerts_success(self):
        """Test: Listar alertas exitosamente"""
        response = self.client.get("/api/alerts/")
        assert response.status_code == status.HTTP_200_OK
        # La API puede devolver un dict con paginación o una lista
        if isinstance(response.data, dict) and "results" in response.data:
            assert len(response.data["results"]) == 2
        else:
            assert isinstance(response.data, list)
            assert len(response.data) == 2

    def test_list_alerts_unread_filter(self):
        """Test: Filtrar solo alertas no leídas"""
        response = self.client.get("/api/alerts/?unread=true")
        assert response.status_code == status.HTTP_200_OK
        # La API puede devolver un dict con paginación o una lista
        if isinstance(response.data, dict) and "results" in response.data:
            results = response.data["results"]
            assert len(results) == 1
            assert results[0]["id"] == self.alert1.id
            assert results[0]["is_read"] is False
        else:
            assert isinstance(response.data, list)
            assert len(response.data) == 1
            assert response.data[0]["id"] == self.alert1.id
            assert response.data[0]["is_read"] is False

    def test_list_alerts_type_warning_filter(self):
        """Test: Filtrar alertas por tipo warning"""
        response = self.client.get("/api/alerts/?type=warning")
        assert response.status_code == status.HTTP_200_OK
        # La API puede devolver un dict con paginación o una lista
        if isinstance(response.data, dict) and "results" in response.data:
            results = response.data["results"]
            assert len(results) == 1
            assert results[0]["alert_type"] == "warning"
        else:
            assert isinstance(response.data, list)
            assert len(response.data) == 1
            assert response.data[0]["alert_type"] == "warning"

    def test_list_alerts_type_exceeded_filter(self):
        """Test: Filtrar alertas por tipo exceeded"""
        response = self.client.get("/api/alerts/?type=exceeded")
        assert response.status_code == status.HTTP_200_OK
        # La API puede devolver un dict con paginación o una lista
        if isinstance(response.data, dict) and "results" in response.data:
            results = response.data["results"]
            assert len(results) == 1
            assert results[0]["alert_type"] == "exceeded"
        else:
            assert isinstance(response.data, list)
            assert len(response.data) == 1
            assert response.data[0]["alert_type"] == "exceeded"

    def test_list_alerts_invalid_type_filter(self):
        """Test: Filtrar con tipo inválido (debe ignorar el filtro)"""
        response = self.client.get("/api/alerts/?type=invalid")
        assert response.status_code == status.HTTP_200_OK
        # Debe devolver todas las alertas ya que el filtro es inválido
        if isinstance(response.data, dict) and "results" in response.data:
            assert len(response.data["results"]) == 2
        else:
            assert len(response.data) == 2

    def test_retrieve_alert_success(self):
        """Test: Obtener detalle de alerta"""
        response = self.client.get(f"/api/alerts/{self.alert1.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == self.alert1.id
        assert response.data["alert_type"] == "warning"

    def test_retrieve_alert_not_found(self):
        """Test: Obtener alerta que no existe"""
        response = self.client.get("/api/alerts/99999/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_alert_other_user(self):
        """Test: No puede obtener alerta de otro usuario"""
        other_user = User.objects.create_user(
            identification="87654321",
            username="otheruser",
            email="other@example.com",
            password="testpass123",
            is_verified=True,
        )
        other_alert = Alert.objects.create(
            user=other_user,
            budget=self.budget,
            alert_type="warning",
            is_read=False,
        )

        response = self.client.get(f"/api/alerts/{other_alert.id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_mark_alert_as_read_success(self):
        """Test: Marcar alerta como leída"""
        data = {"is_read": True}
        response = self.client.patch(f"/api/alerts/{self.alert1.id}/read/", data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "detail" in response.data
        self.alert1.refresh_from_db()
        assert self.alert1.is_read is True

    def test_mark_alert_as_unread_success(self):
        """Test: Marcar alerta como no leída"""
        data = {"is_read": False}
        response = self.client.patch(f"/api/alerts/{self.alert2.id}/read/", data, format="json")
        assert response.status_code == status.HTTP_200_OK
        self.alert2.refresh_from_db()
        assert self.alert2.is_read is False

    def test_mark_all_alerts_as_read_success(self):
        """Test: Marcar todas las alertas como leídas"""
        response = self.client.post("/api/alerts/read-all/")
        assert response.status_code == status.HTTP_200_OK
        assert "success" in response.data
        assert "updated_count" in response.data
        assert response.data["success"] is True
        assert response.data["updated_count"] >= 1

        # Verificar que todas las alertas no leídas ahora están leídas
        self.alert1.refresh_from_db()
        assert self.alert1.is_read is True

    def test_delete_alert_success(self):
        """Test: Eliminar alerta"""
        alert_id = self.alert1.id
        response = self.client.delete(f"/api/alerts/{alert_id}/delete/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Alert.objects.filter(id=alert_id).exists()

    def test_delete_alert_other_user(self):
        """Test: No puede eliminar alerta de otro usuario"""
        other_user = User.objects.create_user(
            identification="87654321",
            username="otheruser2",
            email="other2@example.com",
            password="testpass123",
            is_verified=True,
        )
        other_alert = Alert.objects.create(
            user=other_user,
            budget=self.budget,
            alert_type="warning",
            is_read=False,
        )

        response = self.client.delete(f"/api/alerts/{other_alert.id}/delete/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert Alert.objects.filter(id=other_alert.id).exists()

    def test_list_requires_authentication(self):
        """Test: Listar alertas requiere autenticación"""
        self.client.credentials()
        response = self.client.get("/api/alerts/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_requires_authentication(self):
        """Test: Obtener alerta requiere autenticación"""
        self.client.credentials()
        response = self.client.get(f"/api/alerts/{self.alert1.id}/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_mark_as_read_requires_authentication(self):
        """Test: Marcar como leída requiere autenticación"""
        self.client.credentials()
        data = {"is_read": True}
        response = self.client.patch(f"/api/alerts/{self.alert1.id}/read/", data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_mark_all_as_read_requires_authentication(self):
        """Test: Marcar todas como leídas requiere autenticación"""
        self.client.credentials()
        response = self.client.post("/api/alerts/read-all/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_requires_authentication(self):
        """Test: Eliminar alerta requiere autenticación"""
        self.client.credentials()
        response = self.client.delete(f"/api/alerts/{self.alert1.id}/delete/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
