"""
Tests para gestión de vehículos y SOAT
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta

from vehicles.models import Vehicle, SOAT
from vehicles.services import SOATService
from accounts.models import Account

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
        self.assertEqual(vehicle.plate, "ABC123")
        self.assertTrue(vehicle.is_active)
    
    def test_plate_case_sensitive(self):
        """La placa conserva su formato original"""
        vehicle = Vehicle.objects.create(
            user=self.user,
            plate="abc123",
        )
        self.assertEqual(vehicle.plate, "abc123")


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
        self.assertEqual(soat.status, "vigente")
        self.assertFalse(soat.is_paid)
    
    def test_days_until_expiry(self):
        """Calcular días hasta vencimiento"""
        today = timezone.now().date()
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=today,
            expiry_date=today + timedelta(days=10),
            cost=500000.00,
        )
        self.assertEqual(soat.days_until_expiry, 10)
    
    def test_is_expired(self):
        """Verificar SOAT vencido"""
        today = timezone.now().date()
        soat = SOAT.objects.create(
            vehicle=self.vehicle,
            issue_date=today - timedelta(days=365),
            expiry_date=today - timedelta(days=10),
            cost=500000.00,
        )
        self.assertTrue(soat.is_expired)
    
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
        self.assertTrue(soat.is_near_expiry)


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
            notes="Pago anual"
        )
        
        self.assertIsNotNone(transaction)
        self.soat.refresh_from_db()
        self.assertTrue(self.soat.is_paid)
        self.assertEqual(self.soat.payment_transaction, transaction)


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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["plate"], "API123")
    
    def test_list_vehicles(self):
        """GET /api/vehicles/"""
        Vehicle.objects.create(user=self.user, plate="TEST1")
        Vehicle.objects.create(user=self.user, plate="TEST2")
        
        response = self.client.get("/api/vehicles/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verificar que hay resultados (puede estar paginado)
        if "results" in response.data:
            self.assertEqual(len(response.data["results"]), 2)
        else:
            self.assertEqual(len(response.data), 2)


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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
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
        response = self.client.post(
            f"/api/soats/{soat.id}/register_payment/",
            data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("transaction_id", response.data)
