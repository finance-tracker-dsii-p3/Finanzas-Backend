"""
Tests para gestión de facturas personales
"""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import Account
from bills.models import Bill, BillReminder
from bills.services import BillService
from categories.models import Category
from users.models import UserNotificationPreferences

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
        assert bill.status == Bill.PENDING
        assert not bill.is_paid

    def test_days_until_due(self):
        """Calcular días hasta vencimiento"""
        today = timezone.now().date()
        due_date = today + timedelta(days=5)
        bill = Bill.objects.create(
            user=self.user,
            provider="Internet",
            amount=Decimal("95000.00"),
            due_date=due_date,
        )
        # Usar la propiedad de compatibilidad (puede variar por timezone)
        days = bill.days_until_due_property
        # Debe estar entre 4 y 6 días debido a posibles diferencias de timezone
        assert 4 <= days <= 6

    def test_is_overdue(self):
        """Verificar factura vencida"""
        today = timezone.now().date()
        bill = Bill.objects.create(
            user=self.user,
            provider="EPM",
            amount=Decimal("120000.00"),
            due_date=today - timedelta(days=5),
        )
        # Usar la propiedad de compatibilidad
        assert bill.is_overdue_property

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
        # Usar la propiedad de compatibilidad
        assert bill.is_near_due_property

    def test_update_status(self):
        """Actualizar estado automático"""
        today = timezone.now().date()
        # Crear factura vencida hace varios días para asegurar que esté vencida
        bill = Bill.objects.create(
            user=self.user,
            provider="Disney+",
            amount=Decimal("35000.00"),
            due_date=today - timedelta(days=5),  # Vencida hace 5 días
        )
        # update_status() ahora usa timezone del usuario internamente
        bill.update_status()
        bill.save(update_fields=["status"])
        assert bill.status == Bill.OVERDUE

    def test_days_until_due_with_timezone(self):
        """Calcular días hasta vencimiento usando timezone del usuario"""
        # Crear preferencias de notificación con timezone
        UserNotificationPreferences.objects.create(
            user=self.user,
            timezone="America/Bogota",  # UTC-5
        )
        today = timezone.now().date()
        due_date = today + timedelta(days=10)
        bill = Bill.objects.create(
            user=self.user,
            provider="Internet",
            amount=Decimal("95000.00"),
            due_date=due_date,
        )
        user_tz = self.user.notification_preferences.timezone_object
        days = bill.days_until_due(user_tz=user_tz)
        # Debe estar cerca de 10 días (puede variar por hora del día)
        assert 9 <= days <= 11

    def test_is_overdue_with_timezone(self):
        """Verificar factura vencida usando timezone del usuario"""
        UserNotificationPreferences.objects.create(
            user=self.user,
            timezone="America/Bogota",
        )
        today = timezone.now().date()
        bill = Bill.objects.create(
            user=self.user,
            provider="EPM",
            amount=Decimal("120000.00"),
            due_date=today - timedelta(days=5),
        )
        user_tz = self.user.notification_preferences.timezone_object
        assert bill.is_overdue(user_tz=user_tz)

    def test_is_near_due_with_timezone(self):
        """Verificar factura próxima a vencer usando timezone del usuario"""
        UserNotificationPreferences.objects.create(
            user=self.user,
            timezone="America/Bogota",
        )
        today = timezone.now().date()
        bill = Bill.objects.create(
            user=self.user,
            provider="Claro",
            amount=Decimal("85000.00"),
            due_date=today + timedelta(days=2),
            reminder_days_before=3,
        )
        user_tz = self.user.notification_preferences.timezone_object
        assert bill.is_near_due(user_tz=user_tz)

    def test_update_status_with_timezone(self):
        """Actualizar estado usando timezone del usuario"""
        UserNotificationPreferences.objects.create(
            user=self.user,
            timezone="America/Bogota",
        )
        today = timezone.now().date()
        # Crear factura vencida hace varios días para asegurar que esté vencida
        bill = Bill.objects.create(
            user=self.user,
            provider="Disney+",
            amount=Decimal("35000.00"),
            due_date=today - timedelta(days=5),  # Vencida hace 5 días
        )
        user_tz = self.user.notification_preferences.timezone_object
        bill.update_status(user_tz=user_tz)
        bill.save(update_fields=["status"])
        assert bill.status == Bill.OVERDUE


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
            notes="Pago mensual",
        )

        assert transaction is not None
        self.bill.refresh_from_db()
        assert self.bill.is_paid
        assert self.bill.status == Bill.PAID


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
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["provider"] == "Netflix"

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
        assert response.status_code == status.HTTP_200_OK
        if "results" in response.data:
            assert len(response.data["results"]) == 2
        else:
            assert len(response.data) == 2

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
        response = self.client.post(f"/api/bills/{bill.id}/register_payment/", data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "transaction_id" in response.data

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
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

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
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_filter_by_due_date(self):
        """GET /api/bills/?due_date=YYYY-MM-DD"""
        today = timezone.now().date()
        bill1 = Bill.objects.create(
            user=self.user,
            provider="Netflix",
            amount=Decimal("45000.00"),
            due_date=today + timedelta(days=5),
        )
        Bill.objects.create(
            user=self.user,
            provider="Internet",
            amount=Decimal("95000.00"),
            due_date=today + timedelta(days=10),
        )

        # Filtrar por fecha específica
        response = self.client.get(f"/api/bills/?due_date={bill1.due_date}")
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get("results", response.data)
        assert len(results) == 1
        assert results[0]["id"] == bill1.id

    def test_filter_by_due_date_from(self):
        """GET /api/bills/?due_date_from=YYYY-MM-DD"""
        today = timezone.now().date()
        Bill.objects.create(
            user=self.user,
            provider="Netflix",
            amount=Decimal("45000.00"),
            due_date=today + timedelta(days=5),
        )
        Bill.objects.create(
            user=self.user,
            provider="Internet",
            amount=Decimal("95000.00"),
            due_date=today + timedelta(days=10),
        )

        # Filtrar desde una fecha
        from_date = today + timedelta(days=7)
        response = self.client.get(f"/api/bills/?due_date_from={from_date}")
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get("results", response.data)
        # Solo debe retornar la factura que vence en 10 días
        assert len(results) == 1

    def test_filter_by_due_date_to(self):
        """GET /api/bills/?due_date_to=YYYY-MM-DD"""
        today = timezone.now().date()
        Bill.objects.create(
            user=self.user,
            provider="Netflix",
            amount=Decimal("45000.00"),
            due_date=today + timedelta(days=5),
        )
        Bill.objects.create(
            user=self.user,
            provider="Internet",
            amount=Decimal("95000.00"),
            due_date=today + timedelta(days=10),
        )

        # Filtrar hasta una fecha
        to_date = today + timedelta(days=7)
        response = self.client.get(f"/api/bills/?due_date_to={to_date}")
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get("results", response.data)
        # Solo debe retornar la factura que vence en 5 días
        assert len(results) == 1

    def test_filter_by_due_date_range(self):
        """GET /api/bills/?due_date_from=YYYY-MM-DD&due_date_to=YYYY-MM-DD"""
        today = timezone.now().date()
        Bill.objects.create(
            user=self.user,
            provider="Netflix",
            amount=Decimal("45000.00"),
            due_date=today + timedelta(days=5),
        )
        Bill.objects.create(
            user=self.user,
            provider="Internet",
            amount=Decimal("95000.00"),
            due_date=today + timedelta(days=10),
        )
        Bill.objects.create(
            user=self.user,
            provider="Claro",
            amount=Decimal("85000.00"),
            due_date=today + timedelta(days=15),
        )

        # Filtrar por rango de fechas
        from_date = today + timedelta(days=4)
        to_date = today + timedelta(days=11)
        response = self.client.get(f"/api/bills/?due_date_from={from_date}&due_date_to={to_date}")
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get("results", response.data)
        # Debe retornar las facturas que vencen en 5 y 10 días
        assert len(results) == 2


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
        assert reminder.id is not None
        assert not reminder.is_read

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
        can_create = BillReminder.can_create_reminder(self.bill, BillReminder.UPCOMING)
        assert not can_create

    def test_mark_reminder_read(self):
        """POST /api/bill-reminders/{id}/mark_read/"""
        reminder = BillReminder.objects.create(
            user=self.user,
            bill=self.bill,
            reminder_type=BillReminder.UPCOMING,
            message="Test reminder",
        )

        response = self.client.post(f"/api/bill-reminders/{reminder.id}/mark_read/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_read"]


class BillServiceTimezoneTest(TestCase):
    """Tests para servicios de Bill con timezone"""

    def setUp(self):
        self.user = User.objects.create_user(
            identification="TZ-BILL-001",
            username="tzbill",
            email="tzbill@test.com",
            password="testpass123",
            role="user",
        )
        # Crear preferencias con timezone
        UserNotificationPreferences.objects.create(
            user=self.user,
            timezone="Asia/Kolkata",  # UTC+5:30
        )

    def test_check_and_create_reminders_with_timezone(self):
        """Verificar que las alertas usan timezone del usuario"""
        today = timezone.now().date()
        bill = Bill.objects.create(
            user=self.user,
            provider="Netflix",
            amount=Decimal("45000.00"),
            due_date=today + timedelta(days=1),
            reminder_days_before=7,
        )

        # Ejecutar servicio de recordatorios
        stats = BillService.check_and_create_reminders()

        # Debería haber verificado la factura
        assert stats["total_bills_checked"] >= 1

        # Verificar que se usó el timezone del usuario
        user_tz = self.user.notification_preferences.timezone_object
        days = bill.days_until_due(user_tz=user_tz)
        assert days == 1
