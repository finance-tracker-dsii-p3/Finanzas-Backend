from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import Account


class Transaction(models.Model):
    """
    Modelo para gestionar transacciones financieras
    """

    TYPE_CHOICES = [
        (1, 'Income'),
        (2, 'Expense'),
        (3, 'Transfer'),
        (4, 'Saving'),
    ]

    User = get_user_model()

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name='Usuario',
        help_text='Usuario propietario de la transacción'
    )

    origin_account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='origin_transactions',
        verbose_name='Cuenta',
        help_text='Cuenta asociada a la transacción'
    )

    destination_account = models.ForeignKey(
        Account,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='destination_transactions',
        verbose_name='Cuenta destino',
        help_text='Cuenta destino para transferencias (opcional)'
    )

    type = models.IntegerField(
        choices=TYPE_CHOICES,
        verbose_name='Tipo de transacción',
        help_text='Tipo de la transacción'
        )

    base_amount = models.IntegerField(
        verbose_name='Monto base',
        help_text='Monto base de la transacción'
    )

    tax_percentage = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Impuesto',
        help_text='Porcentaje de impuesto asociado a la transacción (opcional)'
    )

    taxed_amount = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Monto de impuesto',
        help_text='Monto adicional por impuesto (si aplica)'
    )

    total_amount = models.IntegerField(
        verbose_name='Monto total',
        help_text='Monto total de la transacción (incluyendo impuestos)'
    )

    date = models.DateField(
        verbose_name='Fecha',
        help_text='Fecha de la transacción'
    )

    tag = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Etiqueta',
        help_text='Etiqueta asociada a la transacción'
    )

    # HU-12 - Reglas automáticas: Campos adicionales
    description = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Descripción',
        help_text='Descripción del movimiento para aplicar reglas automáticas'
    )

    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
        verbose_name='Categoría',
        help_text='Categoría asignada automáticamente por regla o manualmente'
    )

    applied_rule = models.ForeignKey(
        'rules.AutomaticRule',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applied_transactions',
        verbose_name='Regla aplicada',
        help_text='Regla automática que se aplicó a esta transacción'
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de creación de la transacción"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Fecha de última actualización"
    )


    def save(self, *args, **kwargs):
        # If tax_percentage is provided, compute taxed_amount
        if self.tax_percentage:
            self.taxed_amount = (self.base_amount * (self.tax_percentage / 100))
            self.total_amount = self.base_amount + self.taxed_amount
        else:
            self.taxed_amount = 0
            self.total_amount = self.base_amount

        # HU-12: Aplicar reglas automáticas en transacciones nuevas
        is_new_transaction = self.pk is None
        
        super().save(*args, **kwargs)
        
        # Aplicar reglas automáticas solo si es una transacción nueva
        # y no tiene categoría ni regla asignada manualmente
        if is_new_transaction and not self.category and not self.applied_rule:
            self._apply_automatic_rules()

    def _apply_automatic_rules(self):
        """
        Aplica reglas automáticas a esta transacción.
        Se ejecuta después de save() para evitar problemas de FK.
        """
        try:
            # Importar aquí para evitar dependencias circulares
            from rules.services import RuleEngineService
            
            # Aplicar reglas automáticas
            result = RuleEngineService.apply_rules_to_transaction(self)
            
            # Log del resultado para debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Reglas automáticas en transacción {self.id}: {result['message']}")
            
        except Exception as e:
            # No fallar si hay error aplicando reglas
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error aplicando reglas automáticas a transacción {self.id}: {str(e)}")

    def __str__(self):
        return f"Transacción {self.id} - {self.get_type_display()} - {self.total_amount}"