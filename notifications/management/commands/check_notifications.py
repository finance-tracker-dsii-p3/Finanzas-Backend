"""
Comando para verificar y enviar notificaciones pendientes
Ejecutar diariamente con cron job
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from notifications.engine import NotificationEngine
from bills.services import BillService
from vehicles.services import SOATService


class Command(BaseCommand):
    help = "Verifica y envía notificaciones pendientes: recordatorios personalizados, fin de mes, facturas, SOAT"
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Muestra información detallada',
        )
    
    def handle(self, *args, **options):
        verbose = options.get('verbose', False)
        
        self.stdout.write(self.style.WARNING(
            f"\n{'='*60}\n"
            f"  Verificación de Notificaciones - {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"{'='*60}\n"
        ))
        
        total_notifications = 0
        
        # 1. Verificar recordatorios personalizados pendientes
        self.stdout.write(self.style.HTTP_INFO("\n[1/4] Verificando recordatorios personalizados..."))
        try:
            pending_reminders = NotificationEngine.get_pending_custom_reminders()
            
            for reminder in pending_reminders:
                notification = NotificationEngine.create_custom_reminder_notification(reminder)
                if notification:
                    total_notifications += 1
                    if verbose:
                        self.stdout.write(
                            f"  ✓ Recordatorio enviado: '{reminder.title}' para {reminder.user.username}"
                        )
            
            self.stdout.write(self.style.SUCCESS(
                f"  ✓ {len(pending_reminders)} recordatorios personalizados procesados"
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ✗ Error en recordatorios personalizados: {str(e)}"))
        
        # 2. Verificar recordatorios de fin de mes
        self.stdout.write(self.style.HTTP_INFO("\n[2/4] Verificando recordatorios de fin de mes..."))
        try:
            month_end_notifications = NotificationEngine.check_month_end_reminders()
            total_notifications += len(month_end_notifications)
            
            self.stdout.write(self.style.SUCCESS(
                f"  ✓ {len(month_end_notifications)} recordatorios de fin de mes enviados"
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ✗ Error en recordatorios de fin de mes: {str(e)}"))
        
        # 3. Verificar recordatorios de facturas (esto crea BillReminders y Notifications)
        self.stdout.write(self.style.HTTP_INFO("\n[3/4] Verificando facturas pendientes..."))
        try:
            bill_stats = BillService.check_and_create_reminders()
            
            self.stdout.write(self.style.SUCCESS(
                f"  ✓ Facturas verificadas: {bill_stats['total_bills_checked']}"
            ))
            self.stdout.write(f"    - Próximas a vencer: {bill_stats['upcoming']}")
            self.stdout.write(f"    - Vencen hoy: {bill_stats['due_today']}")
            self.stdout.write(f"    - Atrasadas: {bill_stats['overdue']}")
            
            # Los recordatorios de facturas ya generan notificaciones automáticamente
            total_notifications += bill_stats['reminders_created']
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ✗ Error en recordatorios de facturas: {str(e)}"))
        
        # 4. Verificar alertas de SOAT (esto crea SOATAlerts y Notifications)
        self.stdout.write(self.style.HTTP_INFO("\n[4/4] Verificando SOATs pendientes..."))
        try:
            soat_alerts = SOATService.check_and_create_alerts()
            
            self.stdout.write(self.style.SUCCESS(
                f"  ✓ {len(soat_alerts)} alertas de SOAT creadas"
            ))
            
            if verbose and soat_alerts:
                for alert in soat_alerts:
                    self.stdout.write(
                        f"    - {alert.get_alert_type_display()}: {alert.soat.vehicle.plate}"
                    )
            
            # Las alertas de SOAT ya generan notificaciones automáticamente
            total_notifications += len(soat_alerts)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ✗ Error en alertas de SOAT: {str(e)}"))
        
        # Resumen final
        self.stdout.write(self.style.WARNING(
            f"\n{'='*60}\n"
            f"  Resumen Final\n"
            f"{'='*60}"
        ))
        self.stdout.write(self.style.SUCCESS(
            f"  ✓ Total de notificaciones enviadas: {total_notifications}"
        ))
        self.stdout.write(self.style.WARNING(
            f"\n  Verificación completada exitosamente\n"
            f"{'='*60}\n"
        ))
