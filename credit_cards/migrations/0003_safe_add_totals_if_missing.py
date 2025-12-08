from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("credit_cards", "0002_add_totals"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            ALTER TABLE credit_cards_installmentplan
            ADD COLUMN IF NOT EXISTS total_interest integer NOT NULL DEFAULT 0;
            ALTER TABLE credit_cards_installmentplan
            ADD COLUMN IF NOT EXISTS total_principal integer NOT NULL DEFAULT 0;
            """,
            reverse_sql="""
            ALTER TABLE credit_cards_installmentplan DROP COLUMN IF EXISTS total_interest;
            ALTER TABLE credit_cards_installmentplan DROP COLUMN IF EXISTS total_principal;
            """,
        ),
    ]
