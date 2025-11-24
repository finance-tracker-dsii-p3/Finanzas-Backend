from django.db import models
from django.contrib.auth import get_user_model


class Goal(models.Model):
    """
    Modelo para gestionar metas de ahorro
    """

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

    target_ammount = models.IntegerField(
        verbose_name="Monto objetivo",
        help_text="Monto objetivo de la meta de ahorro",
    )

    saved_ammount = models.IntegerField(
        verbose_name="Monto ahorrado",
        help_text="Monto actualmente ahorrado hacia la meta",
    )

    date = models.DateField(
        verbose_name="Fecha", 
        help_text="Fecha de la meta de ahorro")

    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción adicional de la meta de ahorro (opcional)",
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Fecha de creación de la transacción"
    )

    updated_at = models.DateTimeField(
        auto_now=True, help_text="Fecha de última actualización"
    )

    def save(self, *args, **kwargs):
        # If tax_percentage is provided, compute taxed_amount
        if self.tax_percentage:
            self.taxed_amount = self.base_amount * (self.tax_percentage / 100)
            self.total_amount = self.base_amount + self.taxed_amount
        else:
            self.taxed_amount = 0
            self.total_amount = self.base_amount

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"Transacción {self.id} - {self.get_type_display()} - {self.total_amount}"
        )
