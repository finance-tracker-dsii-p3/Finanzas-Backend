from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APIClient

from users.models import PasswordReset
from users.utils import generate_raw_token, hash_token

User = get_user_model()


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class PasswordResetSimpleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            identification="PR-001",
            username="pr_user",
            email="pr_user@example.com",
            password="oldpass123",
            role="user",
            is_verified=True,
        )

    def test_password_reset_request_success(self):
        """Test solicitud exitosa de restablecimiento de contraseña"""
        url = "/api/auth/password/reset-request/"
        data = {"email": self.user.email}

        response = self.client.post(url, data)

        assert response.status_code == 200
        msg = response.json()["message"]
        assert "Enlace de restablecimiento" in msg or "Si el email existe" in msg

        # Verificar que se creó el registro en la base de datos
        assert PasswordReset.objects.filter(user=self.user).exists()

        # Verificar que se envió el email
        assert len(mail.outbox) == 1
        assert "Restablece tu contraseña" in mail.outbox[0].subject

    def test_password_reset_request_nonexistent_email(self):
        """Test solicitud con email que no existe"""
        url = "/api/auth/password/reset-request/"
        data = {"email": "nonexistent@example.com"}

        response = self.client.post(url, data)

        assert response.status_code == 200
        # Nuevo comportamiento: mensaje explícito
        assert "no existe en la base de datos" in response.json()["message"]

        # No debería crear registro ni enviar email
        assert not PasswordReset.objects.exists()
        assert len(mail.outbox) == 0

    def test_password_reset_confirm_get_valid_token(self):
        """Test GET con token válido devuelve datos del usuario"""
        # Generar token real
        raw_token = generate_raw_token()
        token_hash = hash_token(raw_token)

        # Crear token válido
        PasswordReset.objects.create(
            user=self.user, token_hash=token_hash, expires_at=timezone.now() + timedelta(hours=2)
        )

        url = "/api/auth/password/reset-confirm/"
        response = self.client.get(url, {"token": raw_token})

        assert response.status_code == 200
        data = response.json()
        assert data["valid"]
        assert data["user"]["username"] == self.user.username
        assert data["user"]["email"] == self.user.email

    def test_password_reset_confirm_get_invalid_token(self):
        """Test GET con token inválido"""
        url = "/api/auth/password/reset-confirm/"
        response = self.client.get(url, {"token": "invalid_token"})

        assert response.status_code == 400
        assert "Token inválido" in response.json()["error"]

    def test_password_reset_confirm_get_missing_token(self):
        """Test GET sin token"""
        url = "/api/auth/password/reset-confirm/"
        response = self.client.get(url)

        assert response.status_code == 400
        assert "Token no proporcionado" in response.json()["error"]

    def test_password_reset_confirm_get_expired_token(self):
        """Test GET con token expirado"""
        # Generar token real
        raw_token = generate_raw_token()
        token_hash = hash_token(raw_token)

        # Crear token expirado
        PasswordReset.objects.create(
            user=self.user, token_hash=token_hash, expires_at=timezone.now() - timedelta(hours=1)
        )

        url = "/api/auth/password/reset-confirm/"
        response = self.client.get(url, {"token": raw_token})

        assert response.status_code == 400
        assert "Token expirado o ya usado" in response.json()["error"]

    def test_password_reset_confirm_post_success(self):
        """Test POST exitoso para confirmar restablecimiento"""
        # Generar token real
        raw_token = generate_raw_token()
        token_hash = hash_token(raw_token)

        # Crear token válido
        password_reset = PasswordReset.objects.create(
            user=self.user, token_hash=token_hash, expires_at=timezone.now() + timedelta(hours=2)
        )

        url = "/api/auth/password/reset-confirm/"
        data = {
            "token": raw_token,
            "new_password": "newpass123",
            "new_password_confirm": "newpass123",
        }

        response = self.client.post(url, data)

        assert response.status_code == 200
        assert "Contraseña actualizada" in response.json()["message"]

        # Verificar que la contraseña cambió
        self.user.refresh_from_db()
        assert self.user.check_password("newpass123")

        # Verificar que el token fue marcado como usado
        password_reset.refresh_from_db()
        assert password_reset.is_used()

    def test_password_reset_confirm_post_password_mismatch(self):
        """Test POST con contraseñas que no coinciden"""
        # Generar token real
        raw_token = generate_raw_token()
        token_hash = hash_token(raw_token)

        PasswordReset.objects.create(
            user=self.user, token_hash=token_hash, expires_at=timezone.now() + timedelta(hours=2)
        )

        url = "/api/auth/password/reset-confirm/"
        data = {
            "token": raw_token,
            "new_password": "newpass123",
            "new_password_confirm": "differentpass",
        }

        response = self.client.post(url, data)

        assert response.status_code == 400
        assert "Las contraseñas no coinciden" in str(response.json())

    def test_password_reset_confirm_post_invalid_token(self):
        """Test POST con token inválido"""
        url = "/api/auth/password/reset-confirm/"
        data = {
            "token": "invalid_token",
            "new_password": "newpass123",
            "new_password_confirm": "newpass123",
        }

        response = self.client.post(url, data)

        assert response.status_code == 400
        assert "Token inválido" in str(response.json())

    def test_password_reset_confirm_post_expired_token(self):
        """Test POST con token expirado"""
        # Generar token real
        raw_token = generate_raw_token()
        token_hash = hash_token(raw_token)

        PasswordReset.objects.create(
            user=self.user, token_hash=token_hash, expires_at=timezone.now() - timedelta(hours=1)
        )

        url = "/api/auth/password/reset-confirm/"
        data = {
            "token": raw_token,
            "new_password": "newpass123",
            "new_password_confirm": "newpass123",
        }

        response = self.client.post(url, data)

        assert response.status_code == 400
        assert "Token expirado" in str(response.json())

    def test_password_reset_confirm_post_used_token(self):
        """Test POST con token ya usado"""
        # Generar token real
        raw_token = generate_raw_token()
        token_hash = hash_token(raw_token)

        password_reset = PasswordReset.objects.create(
            user=self.user, token_hash=token_hash, expires_at=timezone.now() + timedelta(hours=2)
        )
        password_reset.mark_as_used()

        url = "/api/auth/password/reset-confirm/"
        data = {
            "token": raw_token,
            "new_password": "newpass123",
            "new_password_confirm": "newpass123",
        }

        response = self.client.post(url, data)

        assert response.status_code == 400
        assert "Token ya fue usado" in str(response.json())

    def test_password_reset_token_expiration(self):
        """Test que los tokens expiran correctamente"""
        password_reset = PasswordReset.objects.create(
            user=self.user, token_hash="test_hash", expires_at=timezone.now() - timedelta(hours=1)
        )

        assert password_reset.is_expired()
        assert not password_reset.is_valid()

    def test_password_reset_token_usage_tracking(self):
        """Test que se puede marcar un token como usado"""
        password_reset = PasswordReset.objects.create(
            user=self.user, token_hash="test_hash", expires_at=timezone.now() + timedelta(hours=2)
        )

        assert not password_reset.is_used()
        password_reset.mark_as_used()
        assert password_reset.is_used()
        assert not password_reset.is_valid()
