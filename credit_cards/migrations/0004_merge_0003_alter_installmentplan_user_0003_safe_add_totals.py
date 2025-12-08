from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("credit_cards", "0003_alter_installmentplan_user"),
        ("credit_cards", "0003_safe_add_totals_if_missing"),
    ]

    operations = []
