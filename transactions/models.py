from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import Account
from decimal import Decimal


class Transaction(models.Model):
    """
    Modelo para gestionar transacciones financieras
    """

    TYPE_CHOICES = [
        (1, "Income"),
        (2, "Expense"),
        (3, "Transfer"),
        (4, "Saving"),
    ]

    User = get_user_model()

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="Usuario",
        help_text="Usuario propietario de la transacción",
    )

    origin_account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="origin_transactions",
        verbose_name="Cuenta",
        help_text="Cuenta asociada a la transacción",
    )

    destination_account = models.ForeignKey(
        Account,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="destination_transactions",
        verbose_name="Cuenta destino",
        help_text="Cuenta destino para transferencias (opcional)",
    )

    category = models.ForeignKey(
        "categories.Category",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="transactions",
        verbose_name="Categoría",
        help_text="Categoría de la transacción (requerida para ingresos y gastos, no aplica para transferencias)",
    )

    type = models.IntegerField(
        choices=TYPE_CHOICES, verbose_name="Tipo de transacción", help_text="Tipo de la transacción"
    )

    base_amount = models.IntegerField(
        verbose_name="Monto base", help_text="Monto base de la transacción"
    )

    tax_percentage = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Impuesto",
        help_text="Porcentaje de impuesto asociado a la transacción (opcional)",
    )

    taxed_amount = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Monto de impuesto",
        help_text="Monto adicional por impuesto (si aplica)",
    )

    gmf_amount = models.IntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name="Monto GMF",
        help_text="Monto del GMF (4x1000) calculado automáticamente si la cuenta no está exenta",
    )

    # Campos para pagos a tarjetas de crédito
    capital_amount = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Monto capital",
        help_text="Monto que va al capital (solo para pagos a tarjetas de crédito). Si no se especifica, se asume que todo el pago es capital.",
    )

    interest_amount = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Monto intereses",
        help_text="Monto que va a intereses (solo para pagos a tarjetas de crédito). Si no se especifica, se calcula automáticamente.",
    )

    total_amount = models.IntegerField(
        verbose_name="Monto total",
        help_text="Monto total de la transacción (incluyendo impuestos y GMF)",
    )

    date = models.DateField(verbose_name="Fecha", help_text="Fecha de la transacción")

    tag = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Etiqueta",
        help_text="Etiqueta asociada a la transacción (ej: #hogar, #viaje)",
    )

    note = models.TextField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name="Nota",
        help_text="Nota descriptiva adicional sobre la transacción",
    )

    # HU-12 - Reglas automáticas: Campos adicionales
    description = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Descripción",
        help_text="Descripción del movimiento para aplicar reglas automáticas",
    )

    applied_rule = models.ForeignKey(
        "rules.AutomaticRule",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="applied_transactions",
        verbose_name="Regla aplicada",
        help_text="Regla automática que se aplicó a esta transacción",
    )

    # HU-11: Relación con metas de ahorro
    goal = models.ForeignKey(
        "goals.Goal",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
        verbose_name="Meta de ahorro",
        help_text="Meta de ahorro a la que se asigna esta transacción (solo para transacciones tipo Saving)",
    )

    # Campos para conversión de moneda
    transaction_currency = models.CharField(
        max_length=3,
        choices=Account.CURRENCY_CHOICES,
        null=True,
        blank=True,
        verbose_name="Moneda de la transacción",
        help_text="Moneda en que se realizó la transacción (si difiere de la cuenta de origen)",
    )

    exchange_rate = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="Tasa de cambio",
        help_text="Tasa de cambio aplicada si hubo conversión de moneda",
    )

    original_amount = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Monto original",
        help_text="Monto original antes de conversión (en centavos de la moneda original)",
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Fecha de creación de la transacción"
    )

    updated_at = models.DateTimeField(auto_now=True, help_text="Fecha de última actualización")

    def save(self, *args, **kwargs):
        # HU-15: Calcular impuestos si no están ya calculados
        # Si taxed_amount ya viene calculado desde el serializer (modo total_amount + tax_percentage),
        # respetarlo. Si no, calcular desde base_amount + tax_percentage (modo tradicional)
        if self.taxed_amount is None:
            # Modo tradicional: calcular impuestos desde base_amount
            if self.tax_percentage:
                self.taxed_amount = int(self.base_amount * (self.tax_percentage / 100))
            else:
                self.taxed_amount = 0

        # Calcular GMF (4x1000 = 0.4%) si aplica
        # El GMF se aplica a:
        # - Gastos (Expense) desde cuentas NO exentas
        # - Transferencias (Transfer) desde cuentas NO exentas
        # - NO se aplica a ingresos (Income)
        # - NO se aplica a tarjetas de crédito
        # - SOLO se aplica a cuentas en pesos colombianos (COP)
        self.gmf_amount = 0

        if self.origin_account and not self.origin_account.gmf_exempt:
            # Verificar si el tipo de transacción requiere GMF
            if self.type in [2, 3]:  # Expense o Transfer
                # NO aplicar GMF a tarjetas de crédito
                if self.origin_account.category != Account.CREDIT_CARD:
                    # GMF solo se aplica a cuentas en pesos colombianos (COP)
                    if self.origin_account.currency == "COP":
                        # GMF = 4x1000 = 0.4% del monto base + impuestos
                        amount_for_gmf = Decimal(str(self.base_amount)) + Decimal(
                            str(self.taxed_amount)
                        )
                        self.gmf_amount = int(amount_for_gmf * Decimal("0.004"))  # 0.4% = 4/1000

        # Calcular total: base + impuestos + GMF
        # El total_amount final siempre incluye GMF si aplica
        self.total_amount = self.base_amount + self.taxed_amount + self.gmf_amount

        # Para pagos a tarjetas de crédito (transferencias donde destino es tarjeta de crédito)
        # Calcular capital e intereses si no se especificaron
        if (
            self.type == 3  # Transfer
            and self.destination_account
            and self.destination_account.category == Account.CREDIT_CARD
        ):
            # Si no se especificó capital_amount, todo el pago es capital
            if self.capital_amount is None:
                self.capital_amount = self.total_amount
                self.interest_amount = 0
            # Si se especificó capital_amount pero no interest_amount, calcular intereses
            elif self.interest_amount is None:
                self.interest_amount = self.total_amount - self.capital_amount
            # Si ambos están especificados, validar que sumen el total
            elif self.capital_amount + self.interest_amount != self.total_amount:
                # Ajustar interest_amount para que sumen el total
                self.interest_amount = self.total_amount - self.capital_amount

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
