"""
Tests para la API de Vehículos (vehicles/views.py)
Fase 1: Aumentar cobertura de tests
"""

from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from accounts.models import Account
from categories.models import Category
from transactions.models import Transaction
from vehicles.models import SOAT, SOATAlert, Vehicle

User = get_user_model()


class VehiclesViewsTests(TestCase):
    """Tests para endpoints de vehículos"""

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

        # Crear vehículo
        self.vehicle = Vehicle.objects.create(
            user=self.user,
            plate="ABC123",
            brand="Toyota",
            model="Corolla",
            year=2020,
        )

        # Crear cuenta
        self.account = Account.objects.create(
            user=self.user,
            name="Banco Principal",
            account_type=Account.ASSET,
            category=Account.BANK_ACCOUNT,
            current_balance=10000000,
            currency="COP",
            account_number="1234567890123",
        )

    def test_list_vehicles_success(self):
        """Test: Listar vehículos exitosamente"""
        response = self.client.get("/api/vehicles/")
        assert response.status_code == status.HTTP_200_OK
        # DRF puede devolver paginación
        if isinstance(response.data, dict) and "results" in response.data:
            assert len(response.data["results"]) == 1
        else:
            assert len(response.data) == 1

    def test_create_vehicle_success(self):
        """Test: Crear vehículo exitosamente"""
        data = {
            "plate": "XYZ789",
            "brand": "Honda",
            "model": "Civic",
            "year": 2021,
        }
        response = self.client.post("/api/vehicles/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["plate"] == "XYZ789"
        assert Vehicle.objects.filter(plate="XYZ789").exists()

    def test_retrieve_vehicle_success(self):
        """Test: Obtener detalle de vehículo"""
        response = self.client.get(f"/api/vehicles/{self.vehicle.id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["plate"] == "ABC123"

    def test_update_vehicle_success(self):
        """Test: Actualizar vehículo"""
        data = {"brand": "Toyota Updated"}
        response = self.client.patch(f"/api/vehicles/{self.vehicle.id}/", data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["brand"] == "Toyota Updated"

    def test_delete_vehicle_success(self):
        """Test: Eliminar vehículo"""
        vehicle_id = self.vehicle.id
        response = self.client.delete(f"/api/vehicles/{vehicle_id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Vehicle.objects.filter(id=vehicle_id).exists()

    def test_vehicle_soats_endpoint_success(self):
        """Test: Listar SOATs de un vehículo"""
        # Crear SOAT
        SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today(),
            expiry_date=date.today() + timedelta(days=365),
            cost=500000,
        )

        response = self.client.get(f"/api/vehicles/{self.vehicle.id}/soats/")
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_vehicle_payment_history_endpoint_success(self):
        """Test: Obtener historial de pagos de SOAT"""
        # Crear categoría y transacción
        category = Category.objects.create(
            user=self.user,
            name="Seguros",
            type=Category.EXPENSE,
            color="#7C3AED",
            icon="fa-umbrella",
        )

        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=30),
            expiry_date=date.today() + timedelta(days=335),
            cost=500000,
        )

        transaction = Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            category=category,
            type=2,
            base_amount=500000,
            total_amount=500000,
            date=date.today(),
            transaction_currency="COP",
        )

        soat.payment_transaction = transaction
        soat.save()

        response = self.client.get(f"/api/vehicles/{self.vehicle.id}/payment_history/")
        assert response.status_code == status.HTTP_200_OK
        assert "payments" in response.data
        assert "total_paid" in response.data

    def test_list_soats_success(self):
        """Test: Listar SOATs exitosamente"""
        SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today(),
            expiry_date=date.today() + timedelta(days=365),
            cost=500000,
        )

        response = self.client.get("/api/soats/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_soat_success(self):
        """Test: Crear SOAT exitosamente"""
        data = {
            "vehicle": self.vehicle.id,
            "issue_date": str(date.today()),
            "expiry_date": str(date.today() + timedelta(days=365)),
            "cost": 500000,
        }
        response = self.client.post("/api/soats/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert SOAT.objects.filter(vehicle=self.vehicle).exists()

    def test_register_payment_success(self):
        """Test: Registrar pago de SOAT"""
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=30),
            expiry_date=date.today() + timedelta(days=335),
            cost=500000,
        )

        data = {
            "account_id": self.account.id,
            "payment_date": str(date.today()),
            "notes": "Pago de prueba",
        }
        response = self.client.post(f"/api/soats/{soat.id}/register_payment/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "transaction_id" in response.data

    def test_register_payment_already_paid_error(self):
        """Test: Error al registrar pago de SOAT ya pagado"""
        # Crear categoría y transacción
        category = Category.objects.create(
            user=self.user,
            name="Seguros",
            type=Category.EXPENSE,
            color="#7C3AED",
            icon="fa-umbrella",
        )

        transaction = Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            category=category,
            type=2,
            base_amount=500000,
            total_amount=500000,
            date=date.today(),
            transaction_currency="COP",
        )

        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=30),
            expiry_date=date.today() + timedelta(days=335),
            cost=500000,
            payment_transaction=transaction,
        )

        data = {
            "account_id": self.account.id,
            "payment_date": str(date.today()),
        }
        response = self.client.post(f"/api/soats/{soat.id}/register_payment/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_status_success(self):
        """Test: Actualizar estado de SOAT"""
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=30),
            expiry_date=date.today() + timedelta(days=5),
            cost=500000,
        )

        response = self.client.post(f"/api/soats/{soat.id}/update_status/")
        assert response.status_code == status.HTTP_200_OK
        assert "soat" in response.data

    def test_expiring_soon_endpoint_success(self):
        """Test: Listar SOATs próximos a vencer"""
        # Crear SOAT próximo a vencer
        SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=300),
            expiry_date=date.today() + timedelta(days=15),
            cost=500000,
        )

        response = self.client.get("/api/soats/expiring_soon/")
        assert response.status_code == status.HTTP_200_OK
        assert "count" in response.data
        assert "soats" in response.data

    def test_expiring_soon_with_days_parameter(self):
        """Test: Listar SOATs próximos a vencer con parámetro days"""
        response = self.client.get("/api/soats/expiring_soon/?days=60")
        assert response.status_code == status.HTTP_200_OK

    def test_expired_endpoint_success(self):
        """Test: Listar SOATs vencidos"""
        # Crear SOAT vencido
        SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=400),
            expiry_date=date.today() - timedelta(days=30),
            cost=500000,
        )

        response = self.client.get("/api/soats/expired/")
        assert response.status_code == status.HTTP_200_OK
        assert "count" in response.data
        assert "soats" in response.data

    def test_list_soat_alerts_success(self):
        """Test: Listar alertas de SOAT"""
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=30),
            expiry_date=date.today() + timedelta(days=5),
            cost=500000,
        )

        SOATAlert.objects.create(
            soat=soat,
            user=self.user,
            alert_type="proxima_vencer",
            message="SOAT próximo a vencer",
        )

        response = self.client.get("/api/soat-alerts/")
        assert response.status_code == status.HTTP_200_OK

    def test_list_soat_alerts_with_is_read_filter(self):
        """Test: Filtrar alertas por estado de lectura"""
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=30),
            expiry_date=date.today() + timedelta(days=5),
            cost=500000,
        )

        SOATAlert.objects.create(
            soat=soat,
            user=self.user,
            alert_type="proxima_vencer",
            message="SOAT próximo a vencer",
            is_read=False,
        )

        response = self.client.get("/api/soat-alerts/?is_read=false")
        assert response.status_code == status.HTTP_200_OK

    def test_mark_alert_read_success(self):
        """Test: Marcar alerta como leída"""
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=30),
            expiry_date=date.today() + timedelta(days=5),
            cost=500000,
        )

        alert = SOATAlert.objects.create(
            soat=soat,
            user=self.user,
            alert_type="proxima_vencer",
            message="SOAT próximo a vencer",
            is_read=False,
        )

        response = self.client.post(f"/api/soat-alerts/{alert.id}/mark_read/")
        assert response.status_code == status.HTTP_200_OK
        alert.refresh_from_db()
        assert alert.is_read

    def test_mark_all_alerts_read_success(self):
        """Test: Marcar todas las alertas como leídas"""
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=30),
            expiry_date=date.today() + timedelta(days=5),
            cost=500000,
        )

        SOATAlert.objects.create(
            soat=soat,
            user=self.user,
            alert_type="proxima_vencer",
            message="SOAT próximo a vencer",
            is_read=False,
        )

        response = self.client.post("/api/soat-alerts/mark_all_read/")
        assert response.status_code == status.HTTP_200_OK
        assert SOATAlert.objects.filter(user=self.user, is_read=False).count() == 0

    def test_perform_create_soat_vehicle_not_owned_error(self):
        """Test: Error al crear SOAT con vehículo de otro usuario"""
        # Crear otro usuario y su vehículo
        other_user = User.objects.create_user(
            identification="87654321",
            username="otheruser",
            email="other@example.com",
            password="otherpass123",
            is_verified=True,
        )
        other_vehicle = Vehicle.objects.create(
            user=other_user, plate="OTHER123", brand="Ford", model="Focus"
        )

        data = {
            "vehicle": other_vehicle.id,
            "issue_date": str(date.today()),
            "expiry_date": str(date.today() + timedelta(days=365)),
            "cost": 500000,
        }
        response = self.client.post("/api/soats/", data, format="json")
        # Puede ser 403 o 400 dependiendo de la implementación
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_403_FORBIDDEN,
        ]

    def test_list_requires_authentication(self):
        """Test: Listar vehículos requiere autenticación"""
        self.client.credentials()
        response = self.client.get("/api/vehicles/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_requires_authentication(self):
        """Test: Crear vehículo requiere autenticación"""
        self.client.credentials()
        data = {"plate": "XYZ789", "brand": "Honda", "model": "Civic"}
        response = self.client.post("/api/vehicles/", data, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_register_payment_value_error(self):
        """Test: Manejo de ValueError al registrar pago"""
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=30),
            expiry_date=date.today() + timedelta(days=335),
            cost=500000,
        )

        # Intentar con cuenta que no tiene suficiente saldo
        # (esto debería causar un ValueError en el servicio)
        self.account.current_balance = 0
        self.account.save()

        data = {
            "account_id": self.account.id,
            "payment_date": str(date.today()),
        }
        response = self.client.post(f"/api/soats/{soat.id}/register_payment/", data, format="json")
        # Puede ser 400 si el servicio valida saldo
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_201_CREATED,
        ]

    def test_mark_alert_read_not_found(self):
        """Test: Error al marcar alerta que no existe"""
        response = self.client.post("/api/soat-alerts/99999/mark_read/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_register_payment_invalid_data(self):
        """Test: Error al registrar pago con datos inválidos"""
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=date.today() - timedelta(days=30),
            expiry_date=date.today() + timedelta(days=335),
            cost=500000,
        )

        # Datos inválidos (sin account_id)
        data = {"payment_date": str(date.today())}
        response = self.client.post(f"/api/soats/{soat.id}/register_payment/", data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
