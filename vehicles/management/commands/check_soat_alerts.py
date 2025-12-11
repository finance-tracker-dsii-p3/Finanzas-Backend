"""
Comando para verificar y crear alertas de SOAT
Ejecutar diariamente con cron: python manage.py check_soat_alerts
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from vehicles.services import SOATService


class Command(BaseCommand):
    help = "Verifica SOATs y crea alertas de vencimiento"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(f"[{timezone.now()}] Iniciando verificación de SOATs...")
        )

        alerts_created = SOATService.check_and_create_alerts()

        self.stdout.write(self.style.SUCCESS(f"✓ Se crearon {len(alerts_created)} alertas nuevas"))

        for alert in alerts_created:
            self.stdout.write(
                f"  - {alert.alert_type}: {alert.soat.vehicle.plate} ({alert.user.username})"
            )

        self.stdout.write(self.style.SUCCESS("Verificación completada exitosamente"))
