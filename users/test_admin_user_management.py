"""
Tests esenciales para gestión completa de usuarios por administradores
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from users.models import User


class AdminUserManagementTestCase(TestCase):
    def setUp(self):
        """Configuración inicial para los tests"""
        # Crear usuarios de prueba
        self.admin_user = User.objects.create_user(
            username="admin_test",
            email="admin@test.com",
            password="testpass123",
            identification="12345678",
            role="admin",
            is_verified=True,
            first_name="Admin",
            last_name="Test",
        )

        self.user_user = User.objects.create_user(
            username="user_test",
            email="user@test.com",
            password="testpass123",
            identification="87654321",
            role="user",
            is_verified=True,
            first_name="user",
            last_name="Test",
            phone="1234567890",
        )

        # Crear usuario no verificado evitando señales
        from django.db import transaction

        with transaction.atomic():
            # Desactivar señales temporalmente
            from django.db.models.signals import post_save

            from users.signals import auto_verify_new_users

            post_save.disconnect(auto_verify_new_users, sender=User)

            self.unverified_user = User.objects.create_user(
                username="unverified_user",
                email="unverified@test.com",
                password="testpass123",
                identification="11223344",
                role="user",
                is_verified=False,
                first_name="Unverified",
                last_name="user",
            )

            # Reconectar señales
            post_save.connect(auto_verify_new_users, sender=User)

        # Crear tokens
        self.admin_token = Token.objects.create(user=self.admin_user)
        self.user_token = Token.objects.create(user=self.user_user)

        self.client = APIClient()

    def test_admin_can_edit_user_info(self):
        """Test: Admin puede editar información básica de useres"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        url = reverse("admin_edit_user", kwargs={"user_id": self.user_user.id})
        data = {
            "first_name": "user Updated",
            "last_name": "Test Updated",
            "email": "user_updated@test.com",
            "phone": "9876543210",
        }
        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert "actualizado exitosamente" in response.data["message"]

        # Verificar que se actualizó
        self.user_user.refresh_from_db()
        assert self.user_user.first_name == "user Updated"
        assert self.user_user.email == "user_updated@test.com"

    def test_admin_cannot_edit_another_admin(self):
        """Test: Admin no puede editar otro admin"""
        another_admin = User.objects.create_user(
            username="admin2",
            email="admin2@test.com",
            password="testpass123",
            identification="99887766",
            role="admin",
            is_verified=True,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        url = reverse("admin_edit_user", kwargs={"user_id": another_admin.id})
        data = {"first_name": "Hacked Admin"}
        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "No se puede editar información de otros administradores" in response.data["error"]

    def test_admin_can_view_user_detail(self):
        """Test: Admin puede ver detalles de un usuario"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        url = reverse("admin_user_detail", kwargs={"user_id": self.user_user.id})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["user"]["username"] == "user_test"
        assert response.data["user"]["role"] == "user"
        assert "date_joined" in response.data["user"]

    def test_admin_users_search_by_role(self):
        """Test: Admin puede filtrar usuarios por rol"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        url = reverse("admin_users_search")
        response = self.client.get(url, {"role": "user"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["users"]) == 2  # 2 useres
        for user in response.data["users"]:
            assert user["role"] == "user"

    def test_admin_users_search_by_verification_status(self):
        """Test: Admin puede filtrar usuarios por estado de verificación"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        url = reverse("admin_users_search")
        response = self.client.get(url, {"is_verified": "false"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["users"]) >= 1
        unverified_users = [u for u in response.data["users"] if not u["is_verified"]]
        assert len(unverified_users) >= 1

    def test_admin_users_search_with_text(self):
        """Test: Admin puede buscar usuarios por texto"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        url = reverse("admin_users_search")
        response = self.client.get(url, {"search": "user_test"})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["users"]) >= 1
        found_user = next((u for u in response.data["users"] if u["username"] == "user_test"), None)
        assert found_user is not None

    def test_user_cannot_access_admin_endpoints(self):
        """Test: user no puede acceder a endpoints de admin"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.user_token.key}")

        # Test edit
        url = reverse("admin_edit_user", kwargs={"user_id": self.user_user.id})
        response = self.client.patch(url, {"first_name": "Hacked"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Test detail
        url = reverse("admin_user_detail", kwargs={"user_id": self.user_user.id})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

        # Test search
        url = reverse("admin_users_search")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_edit_user_invalid_fields(self):
        """Test: Editar usuario con campos completamente inválidos"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        url = reverse("admin_edit_user", kwargs={"user_id": self.user_user.id})
        data = {
            "password": "newpass",  # Campo no permitido
            "username": "newusername",  # Campo no permitido
            "invalid_field": "value",  # Campo inexistente
        }
        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "No se proporcionaron campos válidos" in response.data["error"]

    def test_pagination_in_search(self):
        """Test: Paginación en búsqueda de usuarios"""
        # Crear usuarios adicionales
        for i in range(5):
            User.objects.create_user(
                username=f"test_user_{i}",
                email=f"test{i}@test.com",
                password="testpass123",
                identification=f"1000000{i}",
                role="user",
            )

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        url = reverse("admin_users_search")
        response = self.client.get(url, {"page_size": 3, "page": 1})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["users"]) == 3
        assert "pagination" in response.data
        assert response.data["pagination"]["page"] == 1
        assert response.data["pagination"]["page_size"] == 3

    def test_admin_can_promote_user_via_edit(self):
        """Test: Admin puede ascender user a admin via endpoint edit"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        url = reverse("admin_edit_user", kwargs={"user_id": self.user_user.id})
        data = {"role": "admin"}
        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert "ascendido a admin" in response.data["message"]

        # Verificar que se ascendió
        self.user_user.refresh_from_db()
        assert self.user_user.role == "admin"

    def test_admin_can_verify_user_via_edit(self):
        """Test: Admin puede verificar/desverificar usuario via endpoint edit"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        # Verificar usuario no verificado
        url = reverse("admin_edit_user", kwargs={"user_id": self.unverified_user.id})
        data = {"is_verified": True}
        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert "verificado" in response.data["message"]

        # Verificar que se verificó
        self.unverified_user.refresh_from_db()
        assert self.unverified_user.is_verified
        assert self.unverified_user.verified_by == self.admin_user

    def test_admin_can_unverify_user_via_edit(self):
        """Test: Admin puede desverificar usuario via endpoint edit"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        # Desverificar usuario verificado
        url = reverse("admin_edit_user", kwargs={"user_id": self.user_user.id})
        data = {"is_verified": False}
        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert "desverificado" in response.data["message"]

        # Verificar que se desverificó
        self.user_user.refresh_from_db()
        assert not self.user_user.is_verified
        assert self.user_user.verified_by is None

    def test_admin_can_edit_multiple_fields_at_once(self):
        """Test: Admin puede editar múltiples campos a la vez"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        url = reverse("admin_edit_user", kwargs={"user_id": self.unverified_user.id})
        data = {
            "first_name": "Updated Name",
            "email": "updated@test.com",
            "role": "admin",
            "is_verified": True,
        }
        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert "ascendido a admin" in response.data["message"]
        assert "verificado" in response.data["message"]

        # Verificar todos los cambios
        self.unverified_user.refresh_from_db()
        assert self.unverified_user.first_name == "Updated Name"
        assert self.unverified_user.email == "updated@test.com"
        assert self.unverified_user.role == "admin"
        assert self.unverified_user.is_verified

    def test_invalid_role_change(self):
        """Test: Cambio de rol inválido debe fallar"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        url = reverse("admin_edit_user", kwargs={"user_id": self.user_user.id})
        data = {"role": "invalid_role"}
        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Rol inválido" in response.data["error"]

    def test_invalid_verification_value(self):
        """Test: Valor de verificación inválido debe fallar"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        url = reverse("admin_edit_user", kwargs={"user_id": self.user_user.id})
        data = {"is_verified": "invalid_boolean"}
        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "debe ser true o false" in response.data["error"]

    def test_no_changes_made(self):
        """Test: Sin cambios debe retornar mensaje apropiado"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        url = reverse("admin_edit_user", kwargs={"user_id": self.user_user.id})
        data = {
            "first_name": self.user_user.first_name,  # Mismo valor
            "role": self.user_user.role,  # Mismo valor
            "is_verified": self.user_user.is_verified,  # Mismo valor
        }
        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert "sin cambios realizados" in response.data["message"]

    def test_admin_can_activate_user(self):
        """Test: Admin puede activar un usuario"""
        # Crear usuario inactivo
        inactive_user = User.objects.create_user(
            username="inactive_user",
            email="inactive@test.com",
            password="testpass123",
            identification="22334455",
            role="user",
            is_active=False,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        url = reverse("admin_edit_user", kwargs={"user_id": inactive_user.id})
        data = {"is_active": True}
        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert "activado" in response.data["message"]

        inactive_user.refresh_from_db()
        assert inactive_user.is_active is True

    def test_admin_can_deactivate_user(self):
        """Test: Admin puede desactivar un usuario"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        url = reverse("admin_edit_user", kwargs={"user_id": self.user_user.id})
        data = {"is_active": False}
        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert "desactivado" in response.data["message"]

        self.user_user.refresh_from_db()
        assert self.user_user.is_active is False

    def test_duplicate_email_validation(self):
        """Test: Validación de email duplicado"""
        # Crear otro usuario con email diferente
        another_user = User.objects.create_user(
            username="another_user",
            email="another@test.com",
            password="testpass123",
            identification="33445566",
            role="user",
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        url = reverse("admin_edit_user", kwargs={"user_id": self.user_user.id})
        data = {"email": another_user.email}  # Intentar usar email de otro usuario
        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "ya está en uso por otro usuario" in response.data["error"]

    def test_invalid_email_format_validation(self):
        """Test: Validación de formato de email inválido"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        url = reverse("admin_edit_user", kwargs={"user_id": self.user_user.id})
        data = {"email": "invalid-email-format"}
        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Formato de email inválido" in response.data["error"]

    def test_duplicate_identification_validation(self):
        """Test: Validación de identificación duplicada"""
        # Crear otro usuario con identificación diferente
        another_user = User.objects.create_user(
            username="another_user2",
            email="another2@test.com",
            password="testpass123",
            identification="44556677",
            role="user",
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        url = reverse("admin_edit_user", kwargs={"user_id": self.user_user.id})
        data = {
            "identification": another_user.identification
        }  # Intentar usar identificación de otro usuario
        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "ya está en uso por otro usuario" in response.data["error"]

    def test_audit_log_on_user_edit(self):
        """Test: Auditoría de cambios en edición de usuario"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        url = reverse("admin_edit_user", kwargs={"user_id": self.user_user.id})
        data = {
            "first_name": "New Name",
            "email": "newemail@test.com",
            "is_active": False,
        }
        response = self.client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert "audit_log" in response.data
        assert len(response.data["audit_log"]) > 0

        # Verificar que la auditoría contiene los cambios
        audit_log = response.data["audit_log"]
        field_names = [log["field"] for log in audit_log]
        assert "first_name" in field_names
        assert "email" in field_names
        assert "is_active" in field_names

        # Verificar que cada entrada de auditoría tiene los campos requeridos
        for log_entry in audit_log:
            assert "field" in log_entry
            assert "old_value" in log_entry
            assert "new_value" in log_entry
            assert "changed_by" in log_entry
            assert "changed_at" in log_entry
            assert log_entry["changed_by"] == self.admin_user.username

    def test_list_users_includes_last_login(self):
        """Test: Lista de usuarios incluye last_login"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        url = reverse("admin_users_list")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0

        # Verificar que cada usuario tiene last_login en la respuesta
        for user_data in response.data:
            assert "last_login" in user_data
            assert "date_joined" in user_data
            assert "created_at" in user_data
            assert "is_active" in user_data

    def test_user_detail_includes_all_required_fields(self):
        """Test: Detalle de usuario incluye todos los campos requeridos"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")

        url = reverse("admin_user_detail", kwargs={"user_id": self.user_user.id})
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        user_data = response.data["user"]

        # Verificar campos requeridos según HU-19
        assert "date_joined" in user_data  # Fecha de creación
        assert "last_login" in user_data  # Último acceso
        assert "is_active" in user_data  # Estado (activo/inactivo)
