"""
Tests para el endpoint de eliminación de cuenta propia
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

User = get_user_model()


class DeleteOwnAccountViewTestCase(TestCase):
    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            identification="12345678",
            password="testpass123",
            is_verified=True,
        )
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.url = "/api/auth/profile/delete/"

    def test_delete_own_account_success(self):
        """Test exitoso de eliminación de cuenta propia"""
        # Autenticar usuario
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        # Datos para la eliminación
        data = {"password": "testpass123"}

        # Realizar petición
        response = self.client.delete(self.url, data)

        # Verificaciones
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)
        self.assertIn("user_info", response.data)
        self.assertEqual(response.data["user_info"]["username"], "testuser")
        self.assertEqual(response.data["user_info"]["email"], "test@example.com")

        # Verificar que el usuario fue eliminado de la base de datos
        self.assertFalse(User.objects.filter(id=self.user.id).exists())

    def test_delete_own_account_wrong_password(self):
        """Test con contraseña incorrecta"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        data = {"password": "wrongpassword"}
        response = self.client.delete(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertTrue(User.objects.filter(id=self.user.id).exists())  # Usuario no eliminado

    def test_delete_own_account_missing_password(self):
        """Test sin proporcionar contraseña"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        response = self.client.delete(self.url, {})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(User.objects.filter(id=self.user.id).exists())

    def test_delete_own_account_unauthenticated(self):
        """Test sin autenticación"""
        data = {"password": "testpass123"}
        response = self.client.delete(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(User.objects.filter(id=self.user.id).exists())

    def test_delete_own_account_admin_prevention(self):
        """Test que administradores no puedan eliminar sus cuentas"""
        # Crear usuario admin
        admin_user = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            identification="87654321",
            password="adminpass123",
            is_staff=True,
            is_verified=True,
        )
        admin_token, _ = Token.objects.get_or_create(user=admin_user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {admin_token.key}")

        data = {"password": "adminpass123"}
        response = self.client.delete(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(User.objects.filter(id=admin_user.id).exists())  # Admin no eliminado

    def test_delete_own_account_superuser_prevention(self):
        """Test que superusuarios no puedan eliminar sus cuentas"""
        # Crear superusuario
        super_user = User.objects.create_superuser(
            username="superuser",
            email="super@example.com",
            identification="11111111",
            password="superpass123",
        )
        super_token, _ = Token.objects.get_or_create(user=super_user)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {super_token.key}")

        data = {"password": "superpass123"}
        response = self.client.delete(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(User.objects.filter(id=super_user.id).exists())  # Superuser no eliminado

    def test_delete_own_account_token_invalidated(self):
        """Test que el token se invalide después de eliminar la cuenta"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        data = {"password": "testpass123"}
        response = self.client.delete(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Intentar usar el token después de eliminación
        response = self.client.get("/api/auth/profile/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
