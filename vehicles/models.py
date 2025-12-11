"""
Modelos para gestión de vehículos y SOAT
"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

User = get_user_model()


class Vehicle(models.Model):
    """
    Modelo para registrar vehículos del usuario
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="vehicles",
        verbose_name="Usuario",
        help_text="Usuario propietario del vehículo",
    )

    plate = models.CharField(
        max_length=10, verbose_name="Placa", help_text="Placa del vehículo (ej: ABC123)"
    )

    brand = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Marca",
        help_text="Marca del vehículo (ej: Toyota, Honda)",
    )

    model = models.CharField(
        max_length=50, blank=True, verbose_name="Modelo", help_text="Modelo del vehículo"
    )

    year = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Año", help_text="Año del vehículo"
    )

    is_active = models.BooleanField(
        default=True, verbose_name="Activo", help_text="Indica si el vehículo está activo"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        unique_together = [("user", "plate")]
        ordering = ["-created_at"]
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"

    def __str__(self):
        return f"{self.plate} - {self.brand} {self.model}".strip()

    def clean(self):
        """Validaciones personalizadas"""
        if self.plate:
            self.plate = self.plate.upper().strip()


class SOAT(models.Model):
    """
    Modelo para gestionar el SOAT (Seguro Obligatorio de Accidentes de Tránsito)
    """

    STATUS_CHOICES = [
        ("vigente", "Vigente"),
        ("por_vencer", "Por vencer"),
        ("vencido", "Vencido"),
        ("pendiente_pago", "Pendiente de pago"),
        ("atrasado", "Atrasado"),
    ]

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="soats",
        verbose_name="Vehículo",
        help_text="Vehículo asociado al SOAT",
    )

    issue_date = models.DateField(
        verbose_name="Fecha de emisión", help_text="Fecha en que se emitió el SOAT"
    )

    expiry_date = models.DateField(
        verbose_name="Fecha de vencimiento", help_text="Fecha en que vence el SOAT"
    )

    alert_days_before = models.PositiveIntegerField(
        default=7,
        verbose_name="Días de alerta",
        help_text="Días antes del vencimiento para generar alerta",
    )

    cost = models.IntegerField(
        default=0, verbose_name="Costo (centavos)", help_text="Costo del SOAT en centavos"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="vigente",
        verbose_name="Estado",
        help_text="Estado actual del SOAT",
    )

    payment_transaction = models.OneToOneField(
        "transactions.Transaction",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="soat_payment",
        verbose_name="Transacción de pago",
        help_text="Transacción asociada al pago del SOAT",
    )

    insurance_company = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Aseguradora",
        help_text="Compañía aseguradora que emitió el SOAT",
    )

    policy_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Número de póliza",
        help_text="Número de póliza del SOAT",
    )

    notes = models.TextField(
        blank=True, verbose_name="Notas", help_text="Notas adicionales sobre el SOAT"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        ordering = ["-expiry_date"]
        verbose_name = "SOAT"
        verbose_name_plural = "SOATs"

    def __str__(self):
        return f"SOAT {self.vehicle.plate} - Vence {self.expiry_date}"

    def clean(self):
        """Validaciones personalizadas"""
        if self.issue_date and self.expiry_date:
            if self.expiry_date <= self.issue_date:
                raise ValidationError(
                    {
                        "expiry_date": "La fecha de vencimiento debe ser posterior a la fecha de emisión"
                    }
                )

    @property
    def days_until_expiry(self):
        """Calcula días hasta el vencimiento"""
        if not self.expiry_date:
            return None
        today = timezone.now().date()
        delta = self.expiry_date - today
        return delta.days

    @property
    def is_expired(self):
        """Verifica si el SOAT está vencido"""
        return self.days_until_expiry is not None and self.days_until_expiry < 0

    @property
    def is_near_expiry(self):
        """Verifica si está próximo a vencer"""
        days = self.days_until_expiry
        return days is not None and 0 <= days <= self.alert_days_before

    @property
    def is_paid(self):
        """Verifica si el SOAT ha sido pagado"""
        return self.payment_transaction is not None

    def update_status(self):
        """
        Actualiza el estado del SOAT basado en fechas y pago
        """
        if self.is_expired:
            if not self.is_paid:
                self.status = "atrasado"
            else:
                self.status = "vencido"
        elif self.is_near_expiry:
            if not self.is_paid:
                self.status = "pendiente_pago"
            else:
                self.status = "por_vencer"
        else:
            self.status = "vigente"

        self.save(update_fields=["status", "updated_at"])

    def save(self, *args, **kwargs):
        """Override save para actualizar estado automáticamente"""
        self.full_clean()
        super().save(*args, **kwargs)


class SOATAlert(models.Model):
    """
    Modelo para alertas de SOAT
    """

    ALERT_TYPE_CHOICES = [
        ("proxima_vencer", "Próxima a vencer"),
        ("vencida", "Vencida"),
        ("pendiente_pago", "Pendiente de pago"),
        ("atrasada", "Atrasada"),
    ]

    soat = models.ForeignKey(
        SOAT,
        on_delete=models.CASCADE,
        related_name="alerts",
        verbose_name="SOAT",
        help_text="SOAT asociado a la alerta",
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="soat_alerts",
        verbose_name="Usuario",
        help_text="Usuario que recibe la alerta",
    )

    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPE_CHOICES,
        verbose_name="Tipo de alerta",
        help_text="Tipo de alerta de SOAT",
    )

    message = models.TextField(verbose_name="Mensaje", help_text="Mensaje de la alerta")

    is_read = models.BooleanField(
        default=False, verbose_name="Leída", help_text="Indica si la alerta ha sido leída"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Alerta de SOAT"
        verbose_name_plural = "Alertas de SOAT"

    def __str__(self):
        return f"Alerta {self.alert_type} - {self.soat.vehicle.plate}"
