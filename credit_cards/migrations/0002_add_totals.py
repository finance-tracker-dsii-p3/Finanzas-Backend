from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("credit_cards", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="installmentplan",
            name="total_interest",
            field=models.IntegerField(default=0, help_text="Interés total proyectado en centavos"),
        ),
        migrations.AddField(
            model_name="installmentplan",
            name="total_principal",
            field=models.IntegerField(default=0, help_text="Capital total del plan en centavos"),
        ),
    ]
