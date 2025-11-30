# Generated manually for HU-11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('goals', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='goal',
            old_name='target_ammount',
            new_name='target_amount',
        ),
        migrations.RenameField(
            model_name='goal',
            old_name='saved_ammount',
            new_name='saved_amount',
        ),
        migrations.AlterField(
            model_name='goal',
            name='saved_amount',
            field=models.IntegerField(default=0, help_text='Monto actualmente ahorrado hacia la meta', verbose_name='Monto ahorrado'),
        ),
        migrations.AlterField(
            model_name='goal',
            name='date',
            field=models.DateField(help_text='Fecha objetivo para alcanzar la meta de ahorro', verbose_name='Fecha meta'),
        ),
        migrations.AlterField(
            model_name='goal',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, help_text='Fecha de creación de la meta'),
        ),
    ]

