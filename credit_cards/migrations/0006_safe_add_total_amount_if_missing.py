from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("credit_cards", "0005_add_total_amount"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE credit_cards_installmentplan
            ADD COLUMN IF NOT EXISTS total_amount integer NOT NULL DEFAULT 0;
            """,
            reverse_sql="""
            ALTER TABLE credit_cards_installmentplan DROP COLUMN IF EXISTS total_amount;
            """,
        ),
    ]
