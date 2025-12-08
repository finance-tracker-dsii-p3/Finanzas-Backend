"""
Tests para gestión de facturas personales
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from datetime import timedelta
from decimal import Decimal

from bills.models import Bill, BillReminder
from bills.services import BillService
from accounts.models import Account
from categories.models import Category

User = get_user_model()


class BillModelTest(TestCase):
    """Tests para el modelo Bill"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            identification="BILL-TEST-001",
            username="billuser",
            email="bill@test.com",
            password="testpass123",
            role="user",
        )
        self.category = Category.objects.create(
            user=self.user,
            name="Servicios",
            type=Category.EXPENSE,
        )
    
    def test_create_bill(self):
        """Crear factura básica"""
        today = timezone.now().date()
        bill = Bill.objects.create(
            user=self.user,
            provider="Netflix",
            amount=Decimal("45000.00"),
            due_date=today + timedelta(days=10),
            category=self.category,
        )
        self.assertEqual(bill.status, Bill.PENDING)
        self.assertFalse(bill.is_paid)
    
    def test_days_until_due(self):
        """Calcular días hasta vencimiento"""
        today = timezone.now().date()
        bill = Bill.objects.create(
            user=self.user,
            provider="Internet",
            amount=Decimal("95000.00"),
            due_date=today + timedelta(days=5),
        )
        self.assertEqual(bill.days_until_due, 5)
    
    def test_is_overdue(self):
        """Verificar factura vencida"""
        today = timezone.now().date()
        bill = Bill.objects.create(
            user=self.user,
            provider="EPM",
            amount=Decimal("120000.00"),
            due_date=today - timedelta(days=5),
        )
        self.assertTrue(bill.is_overdue)
    
    def test_is_near_due(self):
        """Verificar factura próxima a vencer"""
        today = timezone.now().date()
        bill = Bill.objects.create(
            user=self.user,
            provider="Claro",
            amount=Decimal("85000.00"),
            due_date=today + timedelta(days=2),
            reminder_days_before=3,
        )
        self.assertTrue(bill.is_near_due)
    
    def test_update_status(self):
        """Actualizar estado automático"""
        today = timezone.now().date()
        bill = Bill.objects.create(
            user=self.user,
            provider="Disney+",
            amount=Decimal("35000.00"),
            due_date=today - timedelta(days=1),
        )
        bill.update_status()
        self.assertEqual(bill.status, Bill.OVERDUE)


class BillServiceTest(TestCase):
    """Tests para servicios de Bill"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            identification="SRV-BILL-001",
            username="srvbill",
            email="srvbill@test.com",
            password="testpass123",
            role="user",
        )
        self.account = Account.objects.create(
            user=self.user,
            name="Cuenta Ahorros",
            bank_name="Bancolombia",
            account_type="asset",
            category="bank_account",
            currency="COP",
            current_balance=Decimal("1000000.00"),
        )
        self.category = Category.objects.create(
            user=self.user,
            name="Servicios",
            type=Category.EXPENSE,
        )
        today = timezone.now().date()
        self.bill = Bill.objects.create(
            user=self.user,
            provider="Netflix",
            amount=Decimal("45000.00"),
            due_date=today + timedelta(days=10),
            category=self.category,
        )
    
    def test_register_payment(self):
        """Registrar pago de factura"""
        transaction = BillService.register_payment(
            bill=self.bill,
            account_id=self.account.id,
            payment_date=timezone.now().date(),
            notes="Pago mensual"
        )
        
        self.assertIsNotNone(transaction)
        self.bill.refresh_from_db()
        self.assertTrue(self.bill.is_paid)
        self.assertEqual(self.bill.status, Bill.PAID)


class BillAPITest(TestCase):
    """Tests para API de facturas"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            identification="API-BILL-001",
            username="apibill",
            email="apibill@test.com",
            password="testpass123",
            role="user",
        )
        self.client.force_authenticate(user=self.user)
        self.account = Account.objects.create(
            user=self.user,
            name="Cuenta Test",
            bank_name="Banco Test",
            account_type="asset",
            category="bank_account",
            currency="COP",
            current_balance=Decimal("1000000.00"),
        )
        self.category = Category.objects.create(
            user=self.user,
            name="Servicios",
            type=Category.EXPENSE,
        )
    
    def test_create_bill(self):
        """POST /api/bills/"""
        today = timezone.now().date()
        data = {
            "provider": "Netflix",
            "amount": 45000.00,
            "due_date": str(today + timedelta(days=10)),
            "category": self.category.id,
            "suggested_account": self.account.id,
        }
        response = self.client.post("/api/bills/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["provider"], "Netflix")
    
    def test_list_bills(self):
        """GET /api/bills/"""
        today = timezone.now().date()
        Bill.objects.create(
            user=self.user,
            provider="Netflix",
            amount=Decimal("45000.00"),
            due_date=today + timedelta(days=10),
        )
        Bill.objects.create(
            user=self.user,
            provider="Internet",
            amount=Decimal("95000.00"),
            due_date=today + timedelta(days=5),
        )
        
        response = self.client.get("/api/bills/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if "results" in response.data:
            self.assertEqual(len(response.data["results"]), 2)
        else:
            self.assertEqual(len(response.data), 2)
    
    def test_register_payment(self):
        """POST /api/bills/{id}/register_payment/"""
        today = timezone.now().date()
        bill = Bill.objects.create(
            user=self.user,
            provider="Netflix",
            amount=Decimal("45000.00"),
            due_date=today + timedelta(days=10),
            category=self.category,
        )
        
        data = {
            "account_id": self.account.id,
            "payment_date": str(today),
            "notes": "Test payment",
        }
        response = self.client.post(
            f"/api/bills/{bill.id}/register_payment/",
            data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("transaction_id", response.data)
    
    def test_pending_bills(self):
        """GET /api/bills/pending/"""
        today = timezone.now().date()
        Bill.objects.create(
            user=self.user,
            provider="Netflix",
            amount=Decimal("45000.00"),
            due_date=today + timedelta(days=10),
            status=Bill.PENDING,
        )
        
        response = self.client.get("/api/bills/pending/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_overdue_bills(self):
        """GET /api/bills/overdue/"""
        today = timezone.now().date()
        bill = Bill.objects.create(
            user=self.user,
            provider="Internet",
            amount=Decimal("95000.00"),
            due_date=today - timedelta(days=5),
        )
        bill.update_status()
        bill.save()
        
        response = self.client.get("/api/bills/overdue/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


class BillReminderTest(TestCase):
    """Tests para recordatorios de facturas"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            identification="REM-TEST-001",
            username="remuser",
            email="rem@test.com",
            password="testpass123",
            role="user",
        )
        self.client.force_authenticate(user=self.user)
        today = timezone.now().date()
        self.bill = Bill.objects.create(
            user=self.user,
            provider="Netflix",
            amount=Decimal("45000.00"),
            due_date=today + timedelta(days=2),
        )
    
    def test_create_reminder(self):
        """Crear recordatorio manualmente"""
        reminder = BillReminder.objects.create(
            user=self.user,
            bill=self.bill,
            reminder_type=BillReminder.UPCOMING,
            message="Test reminder",
        )
        self.assertIsNotNone(reminder.id)
        self.assertFalse(reminder.is_read)
    
    def test_can_create_reminder(self):
        """Validar prevención de duplicados"""
        # Crear primer recordatorio
        BillReminder.objects.create(
            user=self.user,
            bill=self.bill,
            reminder_type=BillReminder.UPCOMING,
            message="Test 1",
        )
        
        # Intentar crear duplicado
        can_create = BillReminder.can_create_reminder(
            self.bill,
            BillReminder.UPCOMING
        )
        self.assertFalse(can_create)
    
    def test_mark_reminder_read(self):
        """POST /api/bill-reminders/{id}/mark_read/"""
        reminder = BillReminder.objects.create(
            user=self.user,
            bill=self.bill,
            reminder_type=BillReminder.UPCOMING,
            message="Test reminder",
        )
        
        response = self.client.post(f"/api/bill-reminders/{reminder.id}/mark_read/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["is_read"])
