from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("credit_cards", "0004_merge_0003_alter_installmentplan_user_0003_safe_add_totals"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name="installmentplan",
                    name="total_amount",
                    field=models.IntegerField(
                        default=0,
                        help_text="Total a pagar (capital + interés) en centavos",
                    ),
                )
            ],
        )
    ]
