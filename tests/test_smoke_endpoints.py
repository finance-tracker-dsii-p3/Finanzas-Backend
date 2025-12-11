from django.test import Client, TestCase


class SmokeEndpointsTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_notifications_list_endpoint_exists(self):
        response = self.client.get("/api/notifications/")
        assert response.status_code != 404

    def test_users_login_endpoint_exists(self):
        response = self.client.get("/api/auth/login/")
        # If it's POST-only it may be 405, but not 404
        assert response.status_code != 404
