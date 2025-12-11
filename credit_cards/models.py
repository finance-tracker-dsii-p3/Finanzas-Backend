from decimal import ROUND_HALF_UP, Decimal

from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from accounts.models import Account
from categories.models import Category
from transactions.models import Transaction

User = get_user_model()


class InstallmentPlan(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Activo"),
        (STATUS_COMPLETED, "Completado"),
        (STATUS_CANCELLED, "Cancelado"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="installment_plans")
    credit_card_account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="installment_plans",
        help_text="Cuenta de tarjeta de crédito asociada",
    )
    purchase_transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name="installment_plans",
        help_text="Transacción de compra que origina el plan",
    )
    description = models.CharField(max_length=255, blank=True)
    purchase_amount = models.IntegerField(help_text="Monto de la compra en centavos")
    number_of_installments = models.PositiveIntegerField(help_text="Número de cuotas")
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Tasa de interés mensual (porcentaje)",
    )
    installment_amount = models.IntegerField(
        null=True,
        blank=True,
        help_text="Valor de la cuota calculada en centavos",
    )
    total_interest = models.IntegerField(
        default=0, help_text="Interés total proyectado en centavos"
    )
    total_principal = models.IntegerField(default=0, help_text="Capital total del plan en centavos")
    total_amount = models.IntegerField(
        default=0, help_text="Total a pagar (capital + interés) en centavos"
    )
    start_date = models.DateField(help_text="Fecha de inicio del plan")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    financing_category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="financing_plans",
        help_text="Categoría usada para registrar intereses/comisiones",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if self.credit_card_account.category != Account.CREDIT_CARD:
            msg = "La cuenta debe ser una tarjeta de crédito."
            raise ValidationError(msg)
        if self.financing_category.type != Category.EXPENSE:
            msg = "La categoría de financiamiento debe ser de gasto."
            raise ValidationError(msg)
        if self.purchase_transaction.user_id != self.user_id:
            msg = "La transacción de compra debe pertenecer al usuario."
            raise ValidationError(msg)
        if self.purchase_transaction.origin_account_id != self.credit_card_account_id:
            msg = "La compra debe haberse hecho con la tarjeta de crédito seleccionada."
            raise ValidationError(msg)
        if self.number_of_installments < 1:
            msg = "El número de cuotas debe ser al menos 1."
            raise ValidationError(msg)
        if self.interest_rate < 0:
            msg = "La tasa de interés no puede ser negativa."
            raise ValidationError(msg)

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.installment_amount is None:
            self.installment_amount = self.calculate_installment_amount()
        schedule = self.get_payment_schedule()
        self.total_interest = sum(item["interest_amount"] for item in schedule)
        self.total_principal = self.purchase_amount
        self.total_amount = sum(item["installment_amount"] for item in schedule)
        super().save(*args, **kwargs)

    def calculate_installment_amount(self):
        principal = Decimal(self.purchase_amount)
        rate = Decimal(self.interest_rate) / Decimal(100)
        n = Decimal(self.number_of_installments)

        if rate == 0:
            installment = principal / n
        else:
            # Sistema francés: A = P * r / (1 - (1+r)^-n)
            r = rate
            installment = principal * r / (Decimal(1) - (Decimal(1) + r) ** (-n))

        return int(installment.quantize(Decimal("1."), rounding=ROUND_HALF_UP))

    def get_payment_schedule(self):
        """Genera calendario con desglose capital/interés y saldo."""
        schedule = []
        principal_remaining = Decimal(self.purchase_amount)
        rate = Decimal(self.interest_rate) / Decimal(100)
        installment_amount = Decimal(self.installment_amount or self.calculate_installment_amount())

        for i in range(1, self.number_of_installments + 1):
            interest_amount = (
                (principal_remaining * rate).quantize(Decimal("1."), rounding=ROUND_HALF_UP)
                if rate > 0
                else Decimal(0)
            )
            principal_amount = installment_amount - interest_amount
            if principal_amount < 0:
                principal_amount = Decimal(0)
            if i == self.number_of_installments:
                principal_amount = principal_remaining
                installment_amt = principal_amount + interest_amount
            else:
                installment_amt = installment_amount

            principal_remaining = principal_remaining - principal_amount
            if principal_remaining < 0:
                principal_remaining = Decimal(0)

            schedule.append(
                {
                    "installment_number": i,
                    "due_date": self.start_date + relativedelta(months=i - 1),
                    "installment_amount": int(installment_amt),
                    "principal_amount": int(principal_amount),
                    "interest_amount": int(interest_amount),
                    "remaining_principal": int(principal_remaining),
                }
            )

        return schedule

    def __str__(self):
        return f"Plan #{self.id} - {self.credit_card_account.name}"


class InstallmentPayment(models.Model):
    STATUS_PENDING = "pending"
    STATUS_COMPLETED = "completed"
    STATUS_OVERDUE = "overdue"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pendiente"),
        (STATUS_COMPLETED, "Pagado"),
        (STATUS_OVERDUE, "Vencido"),
    ]

    plan = models.ForeignKey(InstallmentPlan, on_delete=models.CASCADE, related_name="payments")
    installment_number = models.PositiveIntegerField()
    due_date = models.DateField()
    installment_amount = models.IntegerField(help_text="Valor total de la cuota en centavos")
    principal_amount = models.IntegerField(help_text="Porción de capital en centavos")
    interest_amount = models.IntegerField(help_text="Porción de interés en centavos")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    payment_date = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("plan", "installment_number")]
        ordering = ["installment_number"]

    def save(self, *args, **kwargs):
        self.update_status()
        super().save(*args, **kwargs)

    def update_status(self):
        from datetime import date

        if self.status == self.STATUS_COMPLETED:
            return
        today = date.today()
        if self.payment_date:
            self.status = self.STATUS_COMPLETED
        elif self.due_date < today:
            self.status = self.STATUS_OVERDUE
        else:
            self.status = self.STATUS_PENDING

    def __str__(self):
        return f"Pago cuota {self.installment_number} del plan {self.plan_id}"
