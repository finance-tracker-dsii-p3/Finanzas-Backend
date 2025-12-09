from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
from decimal import Decimal


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("users", "0001_initial"),
        ("accounts", "0005_account_account_number_account_bank_name"),
        ("categories", "0002_alter_category_icon"),
        ("transactions", "0009_add_currency_conversion_fields"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="InstallmentPlan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("description", models.CharField(blank=True, max_length=255)),
                ("purchase_amount", models.IntegerField(help_text="Monto de la compra en centavos")),
                ("number_of_installments", models.PositiveIntegerField(help_text="Número de cuotas")),
                (
                    "interest_rate",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("0.00"),
                        help_text="Tasa de interés mensual (porcentaje)",
                        max_digits=5,
                    ),
                ),
                (
                    "installment_amount",
                    models.IntegerField(blank=True, help_text="Valor de la cuota calculada en centavos", null=True),
                ),
                ("start_date", models.DateField(help_text="Fecha de inicio del plan")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Activo"),
                            ("completed", "Completado"),
                            ("cancelled", "Cancelado"),
                        ],
                        default="active",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "credit_card_account",
                    models.ForeignKey(
                        help_text="Cuenta de tarjeta de crédito asociada",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="installment_plans",
                        to="accounts.account",
                    ),
                ),
                (
                    "financing_category",
                    models.ForeignKey(
                        help_text="Categoría usada para registrar intereses/comisiones",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="financing_plans",
                        to="categories.category",
                    ),
                ),
                (
                    "purchase_transaction",
                    models.ForeignKey(
                        help_text="Transacción de compra que origina el plan",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="installment_plans",
                        to="transactions.transaction",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="installment_plans",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="InstallmentPayment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("installment_number", models.PositiveIntegerField()),
                ("due_date", models.DateField()),
                ("installment_amount", models.IntegerField(help_text="Valor total de la cuota en centavos")),
                ("principal_amount", models.IntegerField(help_text="Porción de capital en centavos")),
                ("interest_amount", models.IntegerField(help_text="Porción de interés en centavos")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pendiente"),
                            ("completed", "Pagado"),
                            ("overdue", "Vencido"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("payment_date", models.DateField(blank=True, null=True)),
                ("notes", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "plan",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to="credit_cards.installmentplan",
                    ),
                ),
            ],
            options={"ordering": ["installment_number"]},
        ),
        migrations.AlterUniqueTogether(
            name="installmentpayment",
            unique_together={("plan", "installment_number")},
        ),
    ]
