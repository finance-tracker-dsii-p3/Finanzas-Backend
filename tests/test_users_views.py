"""
Tests para la API de Usuarios (users/views.py)
Fase 1: Aumentar cobertura de tests
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

User = get_user_model()


class UsersViewsTests(TestCase):
    """Tests para endpoints de usuarios"""

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

    def test_profile_view_success(self):
        """Test: Obtener perfil del usuario"""
        response = self.client.get("/api/auth/profile/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "testuser"
        assert "email" in response.data
        assert "identification" in response.data

    def test_update_profile_view_success(self):
        """Test: Actualizar perfil del usuario"""
        data = {"first_name": "Test", "last_name": "User"}
        response = self.client.patch("/api/auth/profile/update/", data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data

    def test_logout_view_success(self):
        """Test: Cerrar sesión exitosamente"""
        response = self.client.post("/api/auth/logout/")
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data

    def test_change_password_view_success(self):
        """Test: Cambiar contraseña exitosamente"""
        data = {
            "old_password": "testpass123",
            "new_password": "newpass123",
            "new_password_confirm": "newpass123",
        }
        response = self.client.post("/api/auth/change-password/", data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data

    def test_change_password_wrong_old_password(self):
        """Test: Error al cambiar contraseña con contraseña antigua incorrecta"""
        data = {
            "old_password": "wrongpass",
            "new_password": "newpass123",
            "new_password_confirm": "newpass123",
        }
        response = self.client.post("/api/auth/change-password/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_admin_users_list_view_success(self):
        """Test: Admin puede listar usuarios"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.get("/api/auth/admin/users/")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_admin_users_list_view_with_role_filter(self):
        """Test: Filtrar usuarios por rol"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.get("/api/auth/admin/users/?role=user")
        assert response.status_code == status.HTTP_200_OK

    def test_admin_users_list_view_with_verified_filter(self):
        """Test: Filtrar usuarios por estado de verificación"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.get("/api/auth/admin/users/?is_verified=true")
        assert response.status_code == status.HTTP_200_OK

    def test_admin_users_list_view_requires_admin(self):
        """Test: Usuario normal no puede listar usuarios"""
        response = self.client.get("/api/auth/admin/users/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_profile_view_requires_authentication(self):
        """Test: Obtener perfil requiere autenticación"""
        self.client.credentials()
        response = self.client.get("/api/auth/profile/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile_view_requires_authentication(self):
        """Test: Actualizar perfil requiere autenticación"""
        self.client.credentials()
        data = {"first_name": "Test"}
        response = self.client.patch("/api/auth/profile/update/", data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
