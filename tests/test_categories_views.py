"""
Tests para la API de Categorías (categories/views.py)
Fase 1: Aumentar cobertura de tests
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from categories.models import Category

User = get_user_model()


class CategoriesViewsTests(TestCase):
    """Tests para endpoints de categorías"""

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

        # Crear categorías de prueba
        self.expense_category = Category.objects.create(
            user=self.user,
            name="Comida",
            type=Category.EXPENSE,
            color="#DC2626",
            icon="fa-utensils",
            is_active=True,
        )

        self.income_category = Category.objects.create(
            user=self.user,
            name="Salario",
            type=Category.INCOME,
            color="#16A34A",
            icon="fa-dollar-sign",
            is_active=True,
        )

    def test_list_categories_success(self):
        """Test: Listar categorías exitosamente"""
        response = self.client.get("/api/categories/")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) == 2

    def test_list_categories_with_active_only_filter(self):
        """Test: Filtrar solo categorías activas"""
        self.expense_category.is_active = False
        self.expense_category.save()

        response = self.client.get("/api/categories/?active_only=true")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Salario"

    def test_list_categories_with_type_filter(self):
        """Test: Filtrar categorías por tipo"""
        response = self.client.get("/api/categories/?type=expense")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Comida"

    def test_list_categories_empty_message(self):
        """Test: Mensaje cuando no hay categorías"""
        Category.objects.filter(user=self.user).delete()
        response = self.client.get("/api/categories/")
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data
        assert response.data["count"] == 0

    def test_create_category_success(self):
        """Test: Crear categoría exitosamente"""
        data = {
            "name": "Transporte",
            "type": "expense",
            "color": "#EA580C",
            "icon": "fa-car",
        }
        response = self.client.post("/api/categories/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Transporte"
        assert Category.objects.filter(name="Transporte").exists()

    def test_retrieve_category_success(self):
        """Test: Obtener detalle de categoría"""
        response = self.client.get(f"/api/categories/{self.expense_category.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Comida"
        assert response.data["id"] == self.expense_category.id

    def test_update_category_success(self):
        """Test: Actualizar categoría exitosamente"""
        data = {"name": "Comida Actualizada"}
        response = self.client.patch(
            f"/api/categories/{self.expense_category.id}/", data, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Comida Actualizada"
        self.expense_category.refresh_from_db()
        assert self.expense_category.name == "Comida Actualizada"

    def test_delete_category_success(self):
        """Test: Eliminar categoría sin transacciones"""
        category_id = self.expense_category.id
        response = self.client.delete(f"/api/categories/{category_id}/")
        # Puede ser 204 o 200 dependiendo de la implementación
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
        assert not Category.objects.filter(id=category_id).exists()

    def test_delete_with_reassignment_success(self):
        """Test: Eliminar categoría con reasignación"""
        target_category = Category.objects.create(
            user=self.user,
            name="Categoría Destino",
            type=Category.EXPENSE,
            color="#000000",
            icon="fa-shopping-cart",
        )

        data = {"target_category_id": target_category.id}
        response = self.client.post(
            f"/api/categories/{self.expense_category.id}/delete_with_reassignment/",
            data,
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert not Category.objects.filter(id=self.expense_category.id).exists()

    def test_delete_with_reassignment_invalid_target(self):
        """Test: Error con categoría destino inválida"""
        data = {"target_category_id": 99999}
        response = self.client.post(
            f"/api/categories/{self.expense_category.id}/delete_with_reassignment/",
            data,
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_toggle_active_success(self):
        """Test: Activar/desactivar categoría"""
        initial_status = self.expense_category.is_active
        response = self.client.post(f"/api/categories/{self.expense_category.id}/toggle_active/")
        assert response.status_code == status.HTTP_200_OK
        self.expense_category.refresh_from_db()
        assert self.expense_category.is_active != initial_status

    def test_validate_deletion_success(self):
        """Test: Validar eliminación de categoría"""
        response = self.client.get(f"/api/categories/{self.expense_category.id}/validate_deletion/")
        assert response.status_code == status.HTTP_200_OK
        assert "can_delete" in response.data

    def test_stats_endpoint_success(self):
        """Test: Obtener estadísticas de categorías"""
        response = self.client.get("/api/categories/stats/")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, dict)

    def test_bulk_update_order_success(self):
        """Test: Actualizar orden de múltiples categorías"""
        data = {
            "categories": [
                {"id": self.expense_category.id, "order": 1},
                {"id": self.income_category.id, "order": 2},
            ]
        }
        response = self.client.post("/api/categories/bulk_update_order/", data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "updated_count" in response.data

    def test_bulk_update_order_invalid_data(self):
        """Test: Error con datos inválidos en bulk update"""
        data = {"categories": "invalid"}
        response = self.client.post("/api/categories/bulk_update_order/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_income_endpoint_success(self):
        """Test: Obtener solo categorías de ingresos"""
        response = self.client.get("/api/categories/income/")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, (list, dict))
        # Verificar que todas son de tipo income
        if isinstance(response.data, list):
            for cat in response.data:
                assert cat["type"] == "income"

    def test_expense_endpoint_success(self):
        """Test: Obtener solo categorías de gastos"""
        response = self.client.get("/api/categories/expense/")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, (list, dict))
        # Verificar que todas son de tipo expense
        if isinstance(response.data, list):
            for cat in response.data:
                assert cat["type"] == "expense"

    def test_create_defaults_success(self):
        """Test: Crear categorías por defecto cuando no hay categorías"""
        Category.objects.filter(user=self.user).delete()
        response = self.client.post("/api/categories/create_defaults/")
        assert response.status_code == status.HTTP_201_CREATED
        assert "message" in response.data
        assert "categories" in response.data
        assert len(response.data["categories"]) > 0

    def test_create_defaults_when_categories_exist(self):
        """Test: Error al crear defaults cuando ya hay categorías"""
        response = self.client.post("/api/categories/create_defaults/")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    def test_list_requires_authentication(self):
        """Test: Listar categorías requiere autenticación"""
        self.client.credentials()
        response = self.client.get("/api/categories/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_requires_authentication(self):
        """Test: Crear categoría requiere autenticación"""
        self.client.credentials()
        data = {
            "name": "Nueva Categoría",
            "type": "expense",
            "color": "#000000",
            "icon": "fa-tag",
        }
        response = self.client.post("/api/categories/", data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
