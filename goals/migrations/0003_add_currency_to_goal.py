# Generated manually for multiple currencies support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("goals", "0002_rename_amount_fields_and_add_defaults"),
    ]

    operations = [
        migrations.AddField(
            model_name="goal",
            name="currency",
            field=models.CharField(
                choices=[("COP", "Pesos Colombianos"), ("USD", "Dólares"), ("EUR", "Euros")],
                default="COP",
                help_text="Moneda de la meta de ahorro",
                max_length=3,
                verbose_name="Moneda",
            ),
        ),
    ]
