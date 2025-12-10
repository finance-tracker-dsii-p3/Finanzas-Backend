"""
Servicios de negocio para gestión de facturas
"""

from django.db import transaction as db_transaction
from django.utils import timezone
from bills.models import Bill, BillReminder
from accounts.models import Account
from categories.models import Category
from transactions.models import Transaction
from notifications.engine import NotificationEngine


class BillService:
    """Servicio para operaciones de negocio con facturas"""

    @staticmethod
    def register_payment(bill, account_id, payment_date, notes=""):
        """
        Registra el pago de una factura

        Args:
            bill: Instancia de Bill
            account_id: ID de la cuenta desde la cual se paga
            payment_date: Fecha del pago
            notes: Notas opcionales

        Returns:
            Transaction: Transacción creada

        Raises:
            ValueError: Si la factura ya está pagada o la cuenta no existe
        """
        user = bill.user

        # Validar que la factura no esté pagada
        if bill.is_paid:
            raise ValueError("Esta factura ya está pagada")

        # Obtener la cuenta
        try:
            account = Account.objects.get(id=account_id, user=user)
        except Account.DoesNotExist:
            raise ValueError("La cuenta no existe o no te pertenece")

        # Obtener o crear la categoría (usar la de la factura o crear genérica)
        if bill.category:
            category = bill.category
        else:
            # Crear categoría genérica "Servicios" si no existe
            category, _ = Category.objects.get_or_create(
                user=user,
                name="Servicios",
                defaults={
                    "type": Category.EXPENSE,
                    "color": "#10B981",
                    "icon": "fa-file-invoice",
                },
            )

        # Crear transacción con transacción atómica
        with db_transaction.atomic():
            # Convertir monto a centavos (formato interno de Transaction)
            amount_cents = int(bill.amount * 100)

            # Crear la transacción
            txn = Transaction.objects.create(
                user=user,
                origin_account=account,
                category=category,
                type=2,  # Expense
                base_amount=amount_cents,
                date=payment_date,
                description=f"Pago factura {bill.provider}" + (f" - {notes}" if notes else ""),
            )

            # Vincular transacción a la factura
            bill.payment_transaction = txn
            bill.update_status()
            bill.save(update_fields=["payment_transaction", "status"])

            # Actualizar saldo de cuenta
            account.current_balance -= bill.amount
            account.save(update_fields=["current_balance"])

        return txn

    @staticmethod
    def check_and_create_reminders():
        """
        Verifica todas las facturas y crea recordatorios automáticos

        Tipos de recordatorios:
        - upcoming: N días antes del vencimiento
        - due_today: El día del vencimiento
        - overdue: Después del vencimiento sin pagar

        Returns:
            dict: Estadísticas de recordatorios creados
        """
        created_reminders = []

        # Obtener todas las facturas no pagadas
        bills = Bill.objects.filter(status__in=[Bill.PENDING, Bill.OVERDUE])

        for bill in bills:
            days_until_due = bill.days_until_due

            # Recordatorio: Próxima a vencer
            if 0 < days_until_due <= bill.reminder_days_before:
                if BillReminder.can_create_reminder(bill, BillReminder.UPCOMING):
                    reminder = BillReminder.objects.create(
                        user=bill.user,
                        bill=bill,
                        reminder_type=BillReminder.UPCOMING,
                        message=f"La factura de {bill.provider} vence en {days_until_due} día{'s' if days_until_due > 1 else ''} (${bill.amount:,.0f})",
                    )
                    created_reminders.append(reminder)

                    # Crear notificación (HU-18)
                    try:
                        NotificationEngine.create_bill_reminder(
                            user=bill.user, bill=bill, reminder_type="upcoming", days=days_until_due
                        )
                    except Exception:
                        pass

            # Recordatorio: Vence hoy
            elif days_until_due == 0:
                if BillReminder.can_create_reminder(bill, BillReminder.DUE_TODAY):
                    reminder = BillReminder.objects.create(
                        user=bill.user,
                        bill=bill,
                        reminder_type=BillReminder.DUE_TODAY,
                        message=f"La factura de {bill.provider} vence hoy (${bill.amount:,.0f})",
                    )
                    created_reminders.append(reminder)

                    # Crear notificación (HU-18)
                    try:
                        NotificationEngine.create_bill_reminder(
                            user=bill.user, bill=bill, reminder_type="due_today"
                        )
                    except Exception:
                        pass

            # Recordatorio: Atrasada
            elif days_until_due < 0 and bill.status != Bill.PAID:
                if BillReminder.can_create_reminder(bill, BillReminder.OVERDUE):
                    days_overdue = abs(days_until_due)
                    reminder = BillReminder.objects.create(
                        user=bill.user,
                        bill=bill,
                        reminder_type=BillReminder.OVERDUE,
                        message=f"La factura de {bill.provider} está atrasada {days_overdue} día{'s' if days_overdue > 1 else ''} (${bill.amount:,.0f})",
                    )
                    created_reminders.append(reminder)

                    # Crear notificación (HU-18)
                    try:
                        NotificationEngine.create_bill_reminder(
                            user=bill.user, bill=bill, reminder_type="overdue", days=days_overdue
                        )
                    except Exception:
                        pass

                    # Actualizar estado a overdue si no lo está
                    if bill.status != Bill.OVERDUE:
                        bill.status = Bill.OVERDUE
                        bill.save(update_fields=["status"])

        return {
            "total_bills_checked": bills.count(),
            "reminders_created": len(created_reminders),
            "upcoming": len(
                [r for r in created_reminders if r.reminder_type == BillReminder.UPCOMING]
            ),
            "due_today": len(
                [r for r in created_reminders if r.reminder_type == BillReminder.DUE_TODAY]
            ),
            "overdue": len(
                [r for r in created_reminders if r.reminder_type == BillReminder.OVERDUE]
            ),
        }

    @staticmethod
    def mark_reminder_as_read(reminder):
        """
        Marca un recordatorio como leído

        Args:
            reminder: Instancia de BillReminder
        """
        if not reminder.is_read:
            reminder.is_read = True
            reminder.read_at = timezone.now()
            reminder.save(update_fields=["is_read", "read_at"])
