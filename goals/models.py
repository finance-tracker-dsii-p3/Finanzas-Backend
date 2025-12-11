from django.contrib.auth import get_user_model
from django.db import models

from accounts.models import Account


class Goal(models.Model):
    User = get_user_model()

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="goals",
        verbose_name="Usuario",
        help_text="Usuario propietario de la meta de ahorro",
    )

    name = models.CharField(
        max_length=100,
        verbose_name="Nombre de la meta",
        help_text="Nombre descriptivo de la meta de ahorro",
    )

    target_amount = models.IntegerField(
        verbose_name="Monto objetivo",
        help_text="Monto objetivo de la meta de ahorro",
    )

    saved_amount = models.IntegerField(
        default=0,
        verbose_name="Monto ahorrado",
        help_text="Monto actualmente ahorrado hacia la meta",
    )

    date = models.DateField(
        verbose_name="Fecha meta", help_text="Fecha objetivo para alcanzar la meta de ahorro"
    )

    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción adicional de la meta de ahorro (opcional)",
    )

    currency = models.CharField(
        max_length=3,
        choices=Account.CURRENCY_CHOICES,
        default="COP",
        verbose_name="Moneda",
        help_text="Moneda de la meta de ahorro",
    )

    created_at = models.DateTimeField(auto_now_add=True, help_text="Fecha de creación de la meta")

    updated_at = models.DateTimeField(auto_now=True, help_text="Fecha de última actualización")

    def get_progress_percentage(self):
        if self.target_amount == 0:
            return 0.0
        return round((self.saved_amount / self.target_amount) * 100, 2)

    def get_remaining_amount(self):
        remaining = self.target_amount - self.saved_amount
        return max(0, remaining)

    def is_completed(self):
        return self.saved_amount >= self.target_amount

    def __str__(self):
        return f"Meta: {self.name} - {self.saved_amount}/{self.target_amount}"
