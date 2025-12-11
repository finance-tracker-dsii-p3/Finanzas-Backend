from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

User = get_user_model()


class NotificationsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            identification="ID-NOTIF-1",
            username="notifuser",
            email="notif@example.com",
            password="pass12345",
            role="admin",
            is_verified=True,
        )
        # Autenticación por token para endpoints que requieren IsAuthenticated
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_list(self):
        response = self.client.get("/api/notifications/notifications/")
        assert response.status_code == 200

    def test_create_retrieve_update_delete_notification(self):
        # Create
        payload = {
            "user": self.user.id,
            "notification_type": "user_action",
            "title": "Entrada",
            "message": "Usuario realizó una acción",
        }
        create_resp = self.client.post("/api/notifications/notifications/", payload, format="json")
        assert create_resp.status_code == 201
        notif_id = create_resp.data.get("id")
        assert notif_id is not None

        # Retrieve
        retrieve_resp = self.client.get(f"/api/notifications/notifications/{notif_id}/")
        assert retrieve_resp.status_code == 200
        assert retrieve_resp.data["title"] == "Entrada"

        # Update (partial)
        patch_resp = self.client.patch(
            f"/api/notifications/notifications/{notif_id}/",
            {"read": True},
            format="json",
        )
        assert patch_resp.status_code in (200, 202)
        assert patch_resp.data["read"]  # read actualizado

        # Delete
        delete_resp = self.client.delete(f"/api/notifications/notifications/{notif_id}/")
        assert delete_resp.status_code in (204,)

        # Not found after delete
        not_found_resp = self.client.get(f"/api/notifications/notifications/{notif_id}/")
        assert not_found_resp.status_code == 404

    def test_create_invalid_payload_returns_400(self):
        bad_payload = {
            # Falta user y notification_type
            "title": "Sin tipo",
            "message": "Mensaje",
        }
        resp = self.client.post("/api/notifications/notifications/", bad_payload, format="json")
        assert resp.status_code == 400
