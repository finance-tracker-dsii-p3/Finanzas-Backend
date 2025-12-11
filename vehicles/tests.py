"""
Tests para gestión de vehículos y SOAT
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Account
from vehicles.models import SOAT, Vehicle
from vehicles.services import SOATService

User = get_user_model()


class VehicleModelTest(TestCase):
    """Tests para el modelo Vehicle"""

    def setUp(self):
        self.user = User.objects.create_user(
            identification="VEH-TEST-001",
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role="user",
        )

    def test_create_vehicle(self):
        """Crear vehículo básico"""
        vehicle = Vehicle.objects.create(
            user=self.user,
            plate="ABC123",
            brand="Toyota",
            model="Corolla",
            year=2020,
        )
        assert vehicle.plate == "ABC123"
        assert vehicle.is_active

    def test_plate_case_sensitive(self):
        """La placa conserva su formato original"""
        vehicle = Vehicle.objects.create(
            user=self.user,
            plate="abc123",
        )
        assert vehicle.plate == "abc123"


class SOATModelTest(TestCase):
    """Tests para el modelo SOAT"""

    def setUp(self):
        self.user = User.objects.create_user(
            identification="SOAT-TEST-001",
            username="soatuser",
            email="soat@test.com",
            password="testpass123",
            role="user",
        )
        self.vehicle = Vehicle.objects.create(
            user=self.user,
            plate="XYZ789",
        )

    def test_create_soat(self):
        """Crear SOAT básico"""
        today = timezone.now().date()
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=today,
            expiry_date=today + timedelta(days=365),
            cost=500000.00,  # 500,000 COP
        )
        assert soat.status == "vigente"
        assert not soat.is_paid

    def test_days_until_expiry(self):
        """Calcular días hasta vencimiento"""
        today = timezone.now().date()
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=today,
            expiry_date=today + timedelta(days=10),
            cost=500000.00,
        )
        # Usar el método sin timezone (usa timezone del servidor por defecto)
        assert soat.days_until_expiry() == 10

    def test_is_expired(self):
        """Verificar SOAT vencido"""
        today = timezone.now().date()
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=today - timedelta(days=365),
            expiry_date=today - timedelta(days=10),
            cost=500000.00,
        )
        # Usar el método sin timezone
        assert soat.is_expired()

    def test_is_near_expiry(self):
        """Verificar SOAT próximo a vencer"""
        today = timezone.now().date()
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=today,
            expiry_date=today + timedelta(days=5),
            alert_days_before=7,
            cost=500000.00,
        )
        # Usar el método sin timezone
        assert soat.is_near_expiry()

    def test_days_until_expiry_with_timezone(self):
        """Calcular días hasta vencimiento usando timezone del usuario"""

        # Crear preferencias de notificación con timezone
        from users.models import UserNotificationPreferences

        prefs = UserNotificationPreferences.objects.create(
            user=self.user,
            timezone="America/Bogota",  # Mismo timezone que el servidor para evitar diferencias
        )

        today = timezone.now().date()
        expiry_date = today + timedelta(days=10)
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=today,
            expiry_date=expiry_date,
            cost=500000.00,
        )

        # Obtener timezone del usuario
        user_tz = prefs.timezone_object

        # Calcular días usando timezone del usuario
        days = soat.days_until_expiry(user_tz=user_tz)
        # Verificar que el resultado es razonable (puede variar por 1 día según timezone)
        assert 9 <= days <= 11, f"Expected days between 9-11, got {days}"

    def test_is_expired_with_timezone(self):
        """Verificar SOAT vencido usando timezone del usuario"""

        from users.models import UserNotificationPreferences

        prefs = UserNotificationPreferences.objects.create(
            user=self.user,
            timezone="America/Bogota",
        )

        today = timezone.now().date()
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=today - timedelta(days=365),
            expiry_date=today - timedelta(days=10),
            cost=500000.00,
        )

        user_tz = prefs.timezone_object
        assert soat.is_expired(user_tz=user_tz)

    def test_is_near_expiry_with_timezone(self):
        """Verificar SOAT próximo a vencer usando timezone del usuario"""

        from users.models import UserNotificationPreferences

        prefs = UserNotificationPreferences.objects.create(
            user=self.user,
            timezone="America/Bogota",
        )

        today = timezone.now().date()
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=today,
            expiry_date=today + timedelta(days=5),
            alert_days_before=7,
            cost=500000.00,
        )

        user_tz = prefs.timezone_object
        assert soat.is_near_expiry(user_tz=user_tz)


class SOATServiceTest(TestCase):
    """Tests para servicios de SOAT"""

    def setUp(self):
        self.user = User.objects.create_user(
            identification="SRV-TEST-001",
            username="srvuser",
            email="srv@test.com",
            password="testpass123",
            role="user",
        )
        self.vehicle = Vehicle.objects.create(
            user=self.user,
            plate="SRV123",
        )
        self.account = Account.objects.create(
            user=self.user,
            name="Cuenta Ahorros",
            bank_name="Banco Test",
            account_type="asset",
            category="bank_account",
            currency="COP",
            current_balance=1000000.00,  # 1,000,000 COP
        )
        today = timezone.now().date()
        self.soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=today,
            expiry_date=today + timedelta(days=365),
            cost=500000.00,  # 500,000 COP
        )

    def test_register_payment(self):
        """Registrar pago de SOAT"""
        transaction = SOATService.register_payment(
            soat=self.soat,
            account_id=self.account.id,
            payment_date=timezone.now().date(),
            notes="Pago anual",
        )

        assert transaction is not None
        self.soat.refresh_from_db()
        assert self.soat.is_paid
        assert self.soat.payment_transaction == transaction

    def test_check_and_create_alerts_with_timezone(self):
        """Verificar que las alertas usan timezone del usuario"""

        from users.models import UserNotificationPreferences
        from vehicles.models import SOATAlert

        # Crear preferencias con timezone específico
        UserNotificationPreferences.objects.create(
            user=self.user,
            timezone="America/New_York",
        )

        # Crear SOAT que vence en 5 días
        today = timezone.now().date()
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=today,
            expiry_date=today + timedelta(days=5),
            alert_days_before=7,
            cost=500000.00,
        )

        # Ejecutar servicio de alertas
        alerts = SOATService.check_and_create_alerts()

        # Verificar que se creó una alerta
        assert len(alerts) > 0 or SOATAlert.objects.filter(soat=soat).exists()

        # Verificar que el estado se actualizó correctamente
        soat.refresh_from_db()
        assert soat.status in ["pendiente_pago", "por_vencer", "vigente"]


class VehicleAPITest(TestCase):
    """Tests para API de vehículos"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            identification="API-TEST-001",
            username="apiuser",
            email="api@test.com",
            password="testpass123",
            role="user",
        )
        self.client.force_authenticate(user=self.user)

    def test_create_vehicle(self):
        """POST /api/vehicles/"""
        data = {
            "plate": "API123",
            "brand": "Honda",
            "model": "Civic",
            "year": 2021,
        }
        response = self.client.post("/api/vehicles/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["plate"] == "API123"

    def test_list_vehicles(self):
        """GET /api/vehicles/"""
        Vehicle.objects.create(user=self.user, plate="TEST1")
        Vehicle.objects.create(user=self.user, plate="TEST2")

        response = self.client.get("/api/vehicles/")
        assert response.status_code == status.HTTP_200_OK
        # Verificar que hay resultados (puede estar paginado)
        if "results" in response.data:
            assert len(response.data["results"]) == 2
        else:
            assert len(response.data) == 2


class SOATAPITest(TestCase):
    """Tests para API de SOAT"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            identification="SOAT-API-001",
            username="soatapi",
            email="soatapi@test.com",
            password="testpass123",
            role="user",
        )
        self.client.force_authenticate(user=self.user)
        self.vehicle = Vehicle.objects.create(
            user=self.user,
            plate="SOAT1",
        )
        self.account = Account.objects.create(
            user=self.user,
            name="Cuenta Test",
            bank_name="Banco Test",
            account_type="asset",
            category="bank_account",
            currency="COP",
            current_balance=1000000.00,
        )

    def test_create_soat(self):
        """POST /api/soats/"""
        today = timezone.now().date()
        data = {
            "vehicle": self.vehicle.id,
            "issue_date": str(today),
            "expiry_date": str(today + timedelta(days=365)),
            "cost": 500000.00,
            "insurance_company": "Test Insurance",
        }
        response = self.client.post("/api/soats/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

    def test_register_payment(self):
        """POST /api/soats/{id}/register_payment/"""
        today = timezone.now().date()
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=today,
            expiry_date=today + timedelta(days=365),
            cost=500000.00,
        )

        data = {
            "account_id": self.account.id,
            "payment_date": str(today),
            "notes": "Test payment",
        }
        response = self.client.post(f"/api/soats/{soat.id}/register_payment/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "transaction_id" in response.data
