"""
Modelos para gestión de facturas personales (servicios y suscripciones)
"""

import pytz
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

User = get_user_model()


class Bill(models.Model):
    """
    Modelo para facturas de servicios o suscripciones

    Permite registrar facturas con proveedor, monto, fecha de vencimiento,
    cuenta y categoría sugeridas, y realizar seguimiento de su estado.
    """

    # Estados de la factura
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"

    STATUS_CHOICES = [
        (PENDING, "Pendiente"),
        (PAID, "Pagada"),
        (OVERDUE, "Atrasada"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bills",
        verbose_name="Usuario",
        help_text="Usuario propietario de la factura",
    )

    provider = models.CharField(
        max_length=200,
        verbose_name="Proveedor",
        help_text="Nombre del proveedor del servicio o suscripción (ej: Netflix, EPM, Claro)",
    )

    amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="Monto", help_text="Monto total de la factura"
    )

    due_date = models.DateField(
        verbose_name="Fecha de vencimiento", help_text="Fecha límite para pagar la factura"
    )

    suggested_account = models.ForeignKey(
        "accounts.Account",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="suggested_bills",
        verbose_name="Cuenta sugerida",
        help_text="Cuenta desde la cual se sugiere pagar la factura",
    )

    category = models.ForeignKey(
        "categories.Category",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="bills",
        verbose_name="Categoría",
        help_text="Categoría de gasto asociada a la factura",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
        verbose_name="Estado",
        help_text="Estado actual de la factura",
    )

    payment_transaction = models.OneToOneField(
        "transactions.Transaction",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="bill_payment",
        verbose_name="Transacción de pago",
        help_text="Transacción generada al registrar el pago",
    )

    reminder_days_before = models.PositiveIntegerField(
        default=3,
        verbose_name="Días de recordatorio",
        help_text="Días antes del vencimiento para crear recordatorio",
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Descripción",
        help_text="Notas adicionales sobre la factura",
    )

    is_recurring = models.BooleanField(
        default=False,
        verbose_name="Es recurrente",
        help_text="Indica si es una factura que se repite mensualmente",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualización")

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        ordering = ["due_date", "-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["due_date"]),
        ]

    def __str__(self):
        return f"{self.provider} - ${self.amount:,.0f} - {self.due_date}"

    def _get_user_timezone(self):
        """Intenta obtener el objeto timezone del usuario, si no, usa el predeterminado"""
        try:
            return self.user.notification_preferences.timezone_object
        except Exception:
            return pytz.timezone("America/Bogota")  # Default timezone

    def days_until_due(self, user_tz=None):
        """
        Calcula los días restantes hasta el vencimiento usando el timezone del usuario.

        Args:
            user_tz: Objeto timezone del usuario (pytz.timezone). Si es None, intenta obtenerlo del usuario.

        Returns:
            int: Días restantes hasta el vencimiento (puede ser negativo si está vencida)
        """
        if user_tz is None:
            user_tz = self._get_user_timezone()

        if user_tz:
            try:
                user_now = timezone.now().astimezone(user_tz).date()
            except Exception:
                user_now = timezone.now().date()
        else:
            user_now = timezone.now().date()

        delta = self.due_date - user_now
        return delta.days

    @property
    def days_until_due_property(self):
        """Propiedad para compatibilidad con código existente"""
        return self.days_until_due()

    def is_overdue(self, user_tz=None):
        """Verifica si la factura está vencida usando timezone del usuario"""
        if user_tz is None:
            user_tz = self._get_user_timezone()
        days = self.days_until_due(user_tz=user_tz)
        return days < 0 and self.status != self.PAID

    @property
    def is_overdue_property(self):
        """Propiedad para compatibilidad con código existente"""
        return self.is_overdue()

    def is_near_due(self, user_tz=None):
        """Verifica si la factura está próxima a vencer usando timezone del usuario"""
        if user_tz is None:
            user_tz = self._get_user_timezone()
        days = self.days_until_due(user_tz=user_tz)
        return 0 <= days <= self.reminder_days_before and self.status == self.PENDING

    @property
    def is_near_due_property(self):
        """Propiedad para compatibilidad con código existente"""
        return self.is_near_due()

    @property
    def is_paid(self):
        """Verifica si la factura está pagada"""
        return self.status == self.PAID and self.payment_transaction is not None

    def update_status(self, user_tz=None):
        """
        Actualiza el estado de la factura según las reglas usando timezone del usuario:
        - Si está pagada → paid
        - Si está vencida y no pagada → overdue
        - Si no está vencida y no pagada → pending

        Args:
            user_tz: Objeto timezone del usuario (pytz.timezone). Si es None, intenta obtenerlo del usuario.
        """
        if user_tz is None:
            user_tz = self._get_user_timezone()

        if self.payment_transaction:
            self.status = self.PAID
        elif self.is_overdue(user_tz=user_tz):
            self.status = self.OVERDUE
        else:
            self.status = self.PENDING

    def clean(self):
        """Validaciones del modelo"""
        super().clean()

        # Validar que la cuenta sugerida pertenezca al usuario
        if self.suggested_account and self.suggested_account.user != self.user:
            raise ValidationError({"suggested_account": "La cuenta sugerida debe pertenecerte"})

        # Validar que la categoría pertenezca al usuario
        if self.category and self.category.user != self.user:
            raise ValidationError({"category": "La categoría debe pertenecerte"})

        # Validar que el monto sea positivo
        if self.amount and self.amount <= 0:
            raise ValidationError({"amount": "El monto debe ser mayor a cero"})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class BillReminder(models.Model):
    """
    Modelo para recordatorios automáticos de facturas

    Genera alertas cuando una factura está próxima a vencer, vencida o atrasada.
    """

    # Tipos de recordatorio
    UPCOMING = "upcoming"
    DUE_TODAY = "due_today"
    OVERDUE = "overdue"

    REMINDER_TYPE_CHOICES = [
        (UPCOMING, "Próxima a vencer"),
        (DUE_TODAY, "Vence hoy"),
        (OVERDUE, "Atrasada"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bill_reminders", verbose_name="Usuario"
    )

    bill = models.ForeignKey(
        Bill, on_delete=models.CASCADE, related_name="reminders", verbose_name="Factura"
    )

    reminder_type = models.CharField(
        max_length=20, choices=REMINDER_TYPE_CHOICES, verbose_name="Tipo de recordatorio"
    )

    message = models.TextField(verbose_name="Mensaje", help_text="Mensaje del recordatorio")

    is_read = models.BooleanField(default=False, verbose_name="Leído")

    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de lectura")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        verbose_name = "Recordatorio de factura"
        verbose_name_plural = "Recordatorios de facturas"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"]),
            models.Index(fields=["bill", "reminder_type"]),
        ]

    def __str__(self):
        return f"{self.get_reminder_type_display()} - {self.bill.provider}"

    @classmethod
    def can_create_reminder(cls, bill, reminder_type):
        """
        Verifica si se puede crear un recordatorio del tipo especificado
        para evitar duplicados en 24 horas
        """
        last_24h = timezone.now() - timezone.timedelta(hours=24)

        exists = cls.objects.filter(
            bill=bill, reminder_type=reminder_type, created_at__gte=last_24h
        ).exists()

        return not exists
