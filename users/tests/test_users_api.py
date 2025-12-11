from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token

User = get_user_model()


class UsersApiTests(TestCase):
    def setUp(self):
        self.password = "testpass123"
        self.user = User.objects.create_user(
            identification="ID-0001",
            username="user1",
            email="user1@example.com",
            password=self.password,
            role="user",
            is_verified=True,
        )

    def test_login_success(self):
        url = "/api/auth/login/"
        response = self.client.post(url, {"username": "user1", "password": self.password})
        assert response.status_code == 200
        assert "token" in response.json()

    def test_login_invalid_credentials(self):
        url = "/api/auth/login/"
        response = self.client.post(url, {"username": "user1", "password": "wrong"})
        assert response.status_code in (400, 401)

    def test_profile_requires_authentication(self):
        url = "/api/auth/profile/"
        response = self.client.get(url)
        assert response.status_code in (401, 403)

    def test_profile_with_token_and_verified(self):
        token, _ = Token.objects.get_or_create(user=self.user)
        url = "/api/auth/profile/"
        response = self.client.get(url, HTTP_AUTHORIZATION=f"Token {token.key}")
        assert response.status_code == 200

    def test_admin_users_list_requires_admin_auth(self):
        url = "/api/auth/admin/users/"
        # Sin autenticación debe responder 401
        response = self.client.get(url)
        assert response.status_code == 401

    def test_admin_users_list_with_admin_token(self):
        # Crear admin verificado y acceder con token
        admin = User.objects.create_user(
            identification="ID-ADM-1",
            username="admin1",
            email="admin1@example.com",
            password="adminpass123",
            role="admin",
            is_verified=True,
        )
        token, _ = Token.objects.get_or_create(user=admin)
        url = "/api/auth/admin/users/"
        response = self.client.get(url, HTTP_AUTHORIZATION=f"Token {token.key}")
        assert response.status_code == 200
