"""
Management command para verificar facturas y crear recordatorios automáticos
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from bills.services import BillService


class Command(BaseCommand):
    help = "Verifica facturas y crea recordatorios automáticos"

    def handle(self, *args, **options):
        """Ejecutar verificación de facturas"""

        self.stdout.write(
            self.style.SUCCESS(f"[{timezone.now()}] Iniciando verificación de facturas...")
        )

        try:
            # Ejecutar servicio de recordatorios
            stats = BillService.check_and_create_reminders()

            # Mostrar resultados
            self.stdout.write(
                self.style.SUCCESS(f"✓ Se verificaron {stats['total_bills_checked']} facturas")
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Se crearon {stats['reminders_created']} recordatorios nuevos"
                )
            )

            if stats["reminders_created"] > 0:
                self.stdout.write(self.style.WARNING(f"  - Próximas a vencer: {stats['upcoming']}"))
                self.stdout.write(self.style.WARNING(f"  - Vencen hoy: {stats['due_today']}"))
                self.stdout.write(self.style.ERROR(f"  - Atrasadas: {stats['overdue']}"))

            self.stdout.write(self.style.SUCCESS("Verificación completada exitosamente"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"✗ Error durante la verificación: {str(e)}"))
            raise
