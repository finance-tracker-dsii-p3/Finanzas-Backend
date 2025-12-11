import logging
from datetime import date, timedelta
from decimal import Decimal

from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.db import transaction as db_transaction

from accounts.models import Account
from categories.models import Category
from credit_cards.models import InstallmentPayment, InstallmentPlan
from transactions.models import Transaction
from transactions.services import TransactionService

logger = logging.getLogger(__name__)


class InstallmentPlanService:
    @staticmethod
    @db_transaction.atomic
    def create_from_transaction(
        purchase_transaction: Transaction,
        number_of_installments: int,
        interest_rate: Decimal,
        start_date: date,
        financing_category: Category,
        description: str = "",
    ) -> InstallmentPlan:
        user = purchase_transaction.user
        credit_card = purchase_transaction.origin_account

        if credit_card.category != Account.CREDIT_CARD:
            msg = "La transacción no proviene de una tarjeta de crédito."
            raise ValidationError(msg)
        if financing_category.type != Category.EXPENSE:
            msg = "La categoría de financiamiento debe ser de gasto."
            raise ValidationError(msg)
        if financing_category.user_id != user.id:
            msg = "La categoría de financiamiento no pertenece al usuario."
            raise ValidationError(msg)

        plan = InstallmentPlan.objects.create(
            user=user,
            credit_card_account=credit_card,
            purchase_transaction=purchase_transaction,
            description=description or purchase_transaction.description or "Plan de cuotas",
            purchase_amount=purchase_transaction.total_amount,
            number_of_installments=number_of_installments,
            interest_rate=interest_rate,
            start_date=start_date,
            financing_category=financing_category,
        )

        InstallmentPlanService._generate_payments(plan)
        logger.info(f"Plan de cuotas creado #{plan.id} para transacción {purchase_transaction.id}")
        return plan

    @staticmethod
    def _generate_payments(plan: InstallmentPlan):
        """
        Genera todas las cuotas desde cero (uso en creación).
        """
        plan.payments.all().delete()
        InstallmentPlanService._regenerate_future_payments(plan, keep_completed=False)

    @staticmethod
    def _regenerate_future_payments(plan: InstallmentPlan, keep_completed: bool = True):
        """
        Regenera cuotas pendientes/atrasadas a partir del calendario actual.

        - Mantiene cuotas pagadas si keep_completed=True.
        - Recalcula montos y fechas solo para cuotas futuras, evitando tocar pagos ya realizados.
        """
        completed_numbers = set()
        if keep_completed:
            completed_numbers = set(
                plan.payments.filter(status=InstallmentPayment.STATUS_COMPLETED).values_list(
                    "installment_number", flat=True
                )
            )

        # Eliminar cuotas no pagadas para reconstruirlas con el nuevo calendario
        plan.payments.exclude(status=InstallmentPayment.STATUS_COMPLETED).delete()

        schedule = plan.get_payment_schedule()
        payments = []
        for item in schedule:
            # Si keep_completed=True, saltar cuotas ya pagadas
            if keep_completed and item["installment_number"] in completed_numbers:
                continue
            payments.append(
                InstallmentPayment(
                    plan=plan,
                    installment_number=item["installment_number"],
                    due_date=item["due_date"],
                    installment_amount=item["installment_amount"],
                    principal_amount=item["principal_amount"],
                    interest_amount=item["interest_amount"],
                )
            )
        if payments:
            InstallmentPayment.objects.bulk_create(payments)

    @staticmethod
    @db_transaction.atomic
    def record_payment(
        plan: InstallmentPlan,
        installment_number: int,
        payment_date: date,
        source_account: Account,
        notes: str = "",
    ):
        try:
            payment = plan.payments.select_for_update().get(installment_number=installment_number)
        except InstallmentPayment.DoesNotExist:
            msg = "Cuota no encontrada en el plan."
            raise ValidationError(msg)

        if payment.status == InstallmentPayment.STATUS_COMPLETED:
            msg = "La cuota ya está pagada."
            raise ValidationError(msg)

        if source_account.currency != plan.credit_card_account.currency:
            msg = "Las cuentas deben tener la misma moneda."
            raise ValidationError(msg)

        # Crear transferencia para capital (no gasto)
        # IMPORTANTE: Las transferencias banco->tarjeta NO se cuentan como gastos
        # para evitar doble conteo (la compra original ya fue registrada como gasto)
        transfer_tx = Transaction.objects.create(
            user=plan.user,
            origin_account=source_account,
            destination_account=plan.credit_card_account,
            category=None,
            type=TransactionService.TRANSFER,
            base_amount=payment.principal_amount,
            tax_percentage=None,
            taxed_amount=0,
            gmf_amount=0,
            capital_amount=payment.principal_amount,
            interest_amount=0,
            total_amount=payment.principal_amount,
            date=payment_date,
            note=notes,
        )
        # Manejar creación de transacción (actualiza balances pero no valida límites de tarjeta para transferencias)
        try:
            TransactionService.handle_transaction_creation(transfer_tx)
        except ValueError as e:
            # Si falla por validación de límite de tarjeta (saldo positivo), ignorar
            # porque las transferencias de pago pueden dejar saldo positivo temporalmente
            if "saldo positivo" not in str(e).lower():
                raise

        # Crear gasto por interés en categoría de financiamiento
        interest_tx = None
        if payment.interest_amount > 0:
            interest_tx = Transaction.objects.create(
                user=plan.user,
                origin_account=source_account,
                destination_account=None,
                category=plan.financing_category,
                type=TransactionService.EXPENSE,
                base_amount=payment.interest_amount,
                tax_percentage=None,
                taxed_amount=0,
                gmf_amount=0,
                total_amount=payment.interest_amount,
                date=payment_date,
                note=f"Interés cuota {payment.installment_number} - {plan.description}",
            )
            TransactionService.handle_transaction_creation(interest_tx)

        payment.payment_date = payment_date
        payment.notes = notes or payment.notes
        payment.status = InstallmentPayment.STATUS_COMPLETED
        payment.save(update_fields=["payment_date", "notes", "status", "updated_at"])

        InstallmentPlanService._update_plan_status(plan)
        logger.info(
            f"Pago registrado cuota {payment.installment_number} plan {plan.id} - transfer {transfer_tx.id}"
        )
        return payment, transfer_tx, interest_tx

    @staticmethod
    @db_transaction.atomic
    def update_plan(plan: InstallmentPlan, **kwargs) -> InstallmentPlan:
        """
        Actualiza un plan de cuotas, permitiendo edición incluso con cuotas pagadas.
        Solo recalcula cuotas futuras, preservando el histórico de pagos realizados.
        """
        completed_count = plan.payments.filter(status=InstallmentPayment.STATUS_COMPLETED).count()
        requested_installments = kwargs.get("number_of_installments")
        if requested_installments is None:
            requested_installments = plan.number_of_installments

        if requested_installments < 1:
            msg = "El número de cuotas debe ser al menos 1."
            raise ValidationError(msg)

        # No permitir reducir el número de cuotas por debajo de las ya pagadas
        if requested_installments < completed_count:
            msg = f"No puedes reducir las cuotas a menos de las ya pagadas ({completed_count})."
            raise ValidationError(msg)

        allowed_fields = {"number_of_installments", "interest_rate", "start_date", "description"}
        updated = False
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                if field == "start_date" and isinstance(value, str):
                    from datetime import datetime

                    value = datetime.strptime(value, "%Y-%m-%d").date()
                setattr(plan, field, value)
                updated = True

        if updated:
            plan.installment_amount = plan.calculate_installment_amount()
            plan.save()
            # Regenerar solo cuotas futuras, manteniendo histórico pagado
            InstallmentPlanService._regenerate_future_payments(plan, keep_completed=True)
            InstallmentPlanService._update_plan_status(plan)

        return plan

    @staticmethod
    def _update_plan_status(plan: InstallmentPlan):
        total = plan.payments.count()
        completed = plan.payments.filter(status=InstallmentPayment.STATUS_COMPLETED).count()
        if completed == total and total > 0:
            plan.status = InstallmentPlan.STATUS_COMPLETED
        elif plan.status != InstallmentPlan.STATUS_CANCELLED:
            plan.status = InstallmentPlan.STATUS_ACTIVE
        plan.save(update_fields=["status", "updated_at"])

    @staticmethod
    def get_monthly_summary(user, year: int, month: int):
        start = date(year, month, 1)
        end = start + relativedelta(months=1) - timedelta(days=1)
        payments = InstallmentPayment.objects.filter(
            plan__user=user,
            due_date__gte=start,
            due_date__lte=end,
        )
        total = sum(p.installment_amount for p in payments)
        pending = payments.filter(status=InstallmentPayment.STATUS_PENDING).count()
        completed = payments.filter(status=InstallmentPayment.STATUS_COMPLETED).count()

        return {
            "month": f"{year:04d}-{month:02d}",
            "total_installments": payments.count(),
            "total_amount": total,
            "pending_installments": pending,
            "paid_installments": completed,
        }

    @staticmethod
    def get_upcoming_payments(user, days: int = 30):
        today = date.today()
        end = today + timedelta(days=days)
        return InstallmentPayment.objects.filter(
            plan__user=user,
            status__in=[InstallmentPayment.STATUS_PENDING, InstallmentPayment.STATUS_OVERDUE],
            due_date__lte=end,
        ).select_related("plan", "plan__credit_card_account")
