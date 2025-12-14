"""
Tests para servicios de facturas (bills/services.py)
Aumentar cobertura rápidamente
"""

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from accounts.models import Account
from bills.models import Bill, BillReminder
from bills.services import BillService
from categories.models import Category

User = get_user_model()


class BillsServicesTests(TestCase):
    """Tests para servicios de facturas"""

    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            identification="12345678",
            username="testuser",
            email="test@example.com",
            password="testpass123",
            is_verified=True,
        )

        self.account = Account.objects.create(
            user=self.user,
            name="Cuenta Principal",
            account_type=Account.ASSET,
            category=Account.BANK_ACCOUNT,
            current_balance=Decimal("1000000.00"),
            currency="COP",
        )

        self.category = Category.objects.create(
            user=self.user,
            name="Servicios",
            type=Category.EXPENSE,
            color="#DC2626",
        )

        self.bill = Bill.objects.create(
            user=self.user,
            provider="Netflix",
            amount=Decimal("45000.00"),
            due_date=date.today() + timedelta(days=5),
            category=self.category,
        )

    def test_register_payment_success(self):
        """Test: Registrar pago de factura exitosamente"""
        initial_balance = self.account.current_balance
        payment_date = date.today()

        transaction = BillService.register_payment(
            bill=self.bill,
            account_id=self.account.id,
            payment_date=payment_date,
            notes="Pago prueba",
        )

        assert transaction is not None
        assert transaction.type == 2  # Expense
        assert transaction.origin_account == self.account
        self.bill.refresh_from_db()
        assert self.bill.is_paid is True
        self.account.refresh_from_db()
        assert self.account.current_balance < initial_balance

    def test_register_payment_already_paid_error(self):
        """Test: Error al pagar factura ya pagada"""
        # Pagar la factura primero
        BillService.register_payment(
            bill=self.bill,
            account_id=self.account.id,
            payment_date=date.today(),
        )

        # Intentar pagar de nuevo
        try:
            BillService.register_payment(
                bill=self.bill,
                account_id=self.account.id,
                payment_date=date.today(),
            )
            msg = "Debería haber lanzado ValueError"
            raise AssertionError(msg)
        except ValueError as e:
            assert "pagada" in str(e)

    def test_register_payment_invalid_account_error(self):
        """Test: Error con cuenta inválida"""
        try:
            BillService.register_payment(
                bill=self.bill,
                account_id=99999,
                payment_date=date.today(),
            )
            msg = "Debería haber lanzado ValueError"
            raise AssertionError(msg)
        except ValueError as e:
            assert "cuenta" in str(e).lower()

    def test_register_payment_without_category(self):
        """Test: Registrar pago sin categoría (debe crear genérica)"""
        bill_no_category = Bill.objects.create(
            user=self.user,
            provider="Spotify",
            amount=Decimal("20000.00"),
            due_date=date.today() + timedelta(days=3),
            category=None,
        )

        transaction = BillService.register_payment(
            bill=bill_no_category,
            account_id=self.account.id,
            payment_date=date.today(),
        )

        assert transaction.category is not None
        assert transaction.category.name == "Servicios"

    def test_mark_reminder_as_read_success(self):
        """Test: Marcar recordatorio como leído"""
        reminder = BillReminder.objects.create(
            user=self.user,
            bill=self.bill,
            reminder_type=BillReminder.UPCOMING,
            message="Test reminder",
            is_read=False,
        )

        BillService.mark_reminder_as_read(reminder)

        reminder.refresh_from_db()
        assert reminder.is_read is True
        assert reminder.read_at is not None

    def test_mark_reminder_as_read_already_read(self):
        """Test: Marcar recordatorio ya leído (no debe cambiar)"""
        reminder = BillReminder.objects.create(
            user=self.user,
            bill=self.bill,
            reminder_type=BillReminder.UPCOMING,
            message="Test reminder",
            is_read=True,
            read_at=timezone.now() - timedelta(hours=1),
        )

        original_read_at = reminder.read_at

        BillService.mark_reminder_as_read(reminder)

        reminder.refresh_from_db()
        assert reminder.is_read is True
        # No debería cambiar la fecha si ya estaba leído
        assert reminder.read_at == original_read_at

    def test_check_and_create_reminders_upcoming(self):
        """Test: Crear recordatorios para facturas próximas a vencer"""
        # Crear factura que vence en 3 días
        bill_upcoming = Bill.objects.create(
            user=self.user,
            provider="Próxima",
            amount=Decimal("30000.00"),
            due_date=date.today() + timedelta(days=3),
            category=self.category,
            reminder_days_before=5,  # Recordatorio 5 días antes
        )

        result = BillService.check_and_create_reminders()

        assert "total_bills_checked" in result
        assert "reminders_created" in result
        assert result["total_bills_checked"] >= 1

    def test_check_and_create_reminders_due_today(self):
        """Test: Crear recordatorios para facturas que vencen hoy"""
        bill_today = Bill.objects.create(
            user=self.user,
            provider="Vence Hoy",
            amount=Decimal("25000.00"),
            due_date=date.today(),
            category=self.category,
        )

        result = BillService.check_and_create_reminders()

        assert "due_today" in result
        assert result["total_bills_checked"] >= 1

    def test_check_and_create_reminders_overdue(self):
        """Test: Crear recordatorios para facturas atrasadas"""
        bill_overdue = Bill.objects.create(
            user=self.user,
            provider="Atrasada",
            amount=Decimal("40000.00"),
            due_date=date.today() - timedelta(days=3),
            category=self.category,
        )

        result = BillService.check_and_create_reminders()

        assert "overdue" in result
        assert result["total_bills_checked"] >= 1
