# Generated manually for HU-11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("goals", "0002_rename_amount_fields_and_add_defaults"),
        ("transactions", "0007_alter_transaction_category"),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="goal",
            field=models.ForeignKey(
                blank=True,
                help_text="Meta de ahorro a la que se asigna esta transacción (solo para transacciones tipo Saving)",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="transactions",
                to="goals.goal",
                verbose_name="Meta de ahorro",
            ),
        ),
    ]
