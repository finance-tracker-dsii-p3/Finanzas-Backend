from django.db import models
from django.contrib.auth import get_user_model
from budgets.models import Budget


class Alert(models.Model):
    """
    Modelo para gestionar alertas de presupuesto
    """

    ALERT_TYPE_CHOICES = [
        ("warning", "Umbral alcanzado"),
        ("exceeded", "Umbral excedido"),
    ]

    User = get_user_model()

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="alerts",
        verbose_name="Usuario",
        help_text="Usuario propietario de la alerta",
    )

    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name="alerts",
        verbose_name="Presupuesto",
        help_text="Presupuesto asociado a la alerta",
    )

    alert_type = models.CharField(
        max_length=20,
        choices=ALERT_TYPE_CHOICES,
        verbose_name="Tipo de alerta",
        help_text="Tipo de alerta: umbral alcanzado o excedido",
    )

    is_read = models.BooleanField(
        default=False,
        verbose_name="Leída",
        help_text="Indica si la alerta ha sido leída por el usuario",
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de creación de la transacción",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Fecha de última actualización",
    )

    class Meta:
        verbose_name = "Alerta"
        verbose_name_plural = "Alertas"
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Alerta {self.alert_type} para {self.user.username} en presupuesto {self.budget.name}"
        )