# Generated manually for multiple currencies support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("transactions", "0008_transaction_goal"),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="transaction_currency",
            field=models.CharField(
                blank=True,
                choices=[("COP", "Pesos Colombianos"), ("USD", "Dólares"), ("EUR", "Euros")],
                help_text="Moneda en que se realizó la transacción (si difiere de la cuenta de origen)",
                max_length=3,
                null=True,
                verbose_name="Moneda de la transacción",
            ),
        ),
        migrations.AddField(
            model_name="transaction",
            name="exchange_rate",
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                help_text="Tasa de cambio aplicada si hubo conversión de moneda",
                max_digits=10,
                null=True,
                verbose_name="Tasa de cambio",
            ),
        ),
        migrations.AddField(
            model_name="transaction",
            name="original_amount",
            field=models.IntegerField(
                blank=True,
                help_text="Monto original antes de conversión (en centavos de la moneda original)",
                null=True,
                verbose_name="Monto original",
            ),
        ),
    ]
