"""
Servicios para gestión de SOAT y alertas
"""

from django.utils import timezone
from django.db import transaction as db_transaction
from vehicles.models import SOAT, SOATAlert
from transactions.models import Transaction
from accounts.models import Account
from categories.models import Category
from notifications.engine import NotificationEngine
from decimal import Decimal


class SOATService:
    """
    Servicio para operaciones de negocio relacionadas con SOAT
    """
    
    @staticmethod
    def register_payment(soat: SOAT, account_id: int, payment_date, notes: str = ""):
        """
        Registra el pago de un SOAT creando una transacción
        
        Args:
            soat: Instancia de SOAT
            account_id: ID de la cuenta desde la que se paga
            payment_date: Fecha del pago
            notes: Notas adicionales
        
        Returns:
            Transaction: Transacción creada
        
        Raises:
            ValueError: Si el SOAT ya está pagado o la cuenta no existe
        """
        if soat.is_paid:
            raise ValueError("Este SOAT ya ha sido pagado")
        
        user = soat.vehicle.user
        
        try:
            account = Account.objects.get(id=account_id, user=user)
        except Account.DoesNotExist:
            raise ValueError("La cuenta no existe o no te pertenece")
        
        # Buscar o crear categoría "Seguros/Vehículo"
        category, _ = Category.objects.get_or_create(
            user=user,
            name="Seguros",
            defaults={
                "type": Category.EXPENSE,
                "color": "#7C3AED",
                "icon": "fa-umbrella",
            }
        )
        
        # Crear transacción
        with db_transaction.atomic():
            txn = Transaction.objects.create(
                user=user,
                origin_account=account,
                category=category,
                type=2,  # Expense
                base_amount=soat.cost,
                total_amount=soat.cost,
                date=payment_date,
                description=f"Pago SOAT {soat.vehicle.plate} - Vigencia {soat.expiry_date.year}",
                note=notes,
                transaction_currency=account.currency,
            )
            
            # Vincular transacción al SOAT
            soat.payment_transaction = txn
            soat.update_status()
            soat.save(update_fields=["payment_transaction", "status"])
            
            # Actualizar saldo de cuenta
            account.current_balance -= soat.cost
            account.save(update_fields=["current_balance"])
        
        return txn
    
    @staticmethod
    def check_and_create_alerts():
        """
        Verifica todos los SOATs y crea alertas necesarias
        (Para ejecutar con cron job)
        """
        today = timezone.now().date()
        created_alerts = []
        
        # Obtener todos los SOATs activos
        soats = SOAT.objects.select_related("vehicle", "vehicle__user").all()
        
        for soat in soats:
            user = soat.vehicle.user
            days = soat.days_until_expiry
            
            # Actualizar estado
            soat.update_status()
            
            # Verificar si ya existe una alerta reciente (últimas 24 horas)
            recent_alert = SOATAlert.objects.filter(
                soat=soat,
                created_at__gte=timezone.now() - timezone.timedelta(hours=24)
            ).exists()
            
            if recent_alert:
                continue
            
            alert_type = None
            message = None
            
            # Determinar tipo de alerta
            if soat.status == "atrasado":
                alert_type = "atrasada"
                message = f"El SOAT de tu vehículo {soat.vehicle.plate} está vencido y sin pagar desde {soat.expiry_date}. Por favor, realiza el pago lo antes posible."
            
            elif soat.status == "vencido":
                alert_type = "vencida"
                message = f"El SOAT de tu vehículo {soat.vehicle.plate} venció el {soat.expiry_date}. Recuerda renovarlo pronto."
            
            elif soat.status == "pendiente_pago" and days is not None and days <= soat.alert_days_before:
                alert_type = "pendiente_pago"
                if days == 0:
                    message = f"El SOAT de tu vehículo {soat.vehicle.plate} vence HOY. ¡No olvides pagarlo!"
                elif days == 1:
                    message = f"El SOAT de tu vehículo {soat.vehicle.plate} vence MAÑANA. ¡No olvides pagarlo!"
                else:
                    message = f"El SOAT de tu vehículo {soat.vehicle.plate} vence en {days} días ({soat.expiry_date}). ¡No olvides pagarlo!"
            
            elif soat.status == "por_vencer" and days is not None and days <= soat.alert_days_before:
                alert_type = "proxima_vencer"
                if days == 0:
                    message = f"El SOAT de tu vehículo {soat.vehicle.plate} vence HOY."
                elif days == 1:
                    message = f"El SOAT de tu vehículo {soat.vehicle.plate} vence MAÑANA."
                else:
                    message = f"El SOAT de tu vehículo {soat.vehicle.plate} vencerá en {days} días ({soat.expiry_date})."
            
            # Crear alerta si aplica
            if alert_type and message:
                alert = SOATAlert.objects.create(
                    soat=soat,
                    user=user,
                    alert_type=alert_type,
                    message=message
                )
                created_alerts.append(alert)
                
                # Crear notificación (HU-18)
                try:
                    # Mapear tipo de alerta a formato de NotificationEngine
                    if alert_type in ["atrasada", "vencida"]:
                        NotificationEngine.create_soat_reminder(
                            user=user,
                            soat=soat,
                            alert_type="expired",
                            days=abs(days) if days else 0
                        )
                    elif alert_type in ["pendiente_pago", "proxima_vencer"]:
                        if days is not None and days <= 7:
                            NotificationEngine.create_soat_reminder(
                                user=user,
                                soat=soat,
                                alert_type="due_soon",
                                days=days
                            )
                        else:
                            NotificationEngine.create_soat_reminder(
                                user=user,
                                soat=soat,
                                alert_type="upcoming",
                                days=days
                            )
                except:
                    pass
        
        return created_alerts
    
    @staticmethod
    def get_payment_history(vehicle):
        """
        Obtiene el historial de pagos de SOAT de un vehículo
        
        Args:
            vehicle: Instancia de Vehicle
        
        Returns:
            QuerySet: Transacciones de pago de SOAT
        """
        soat_ids = vehicle.soats.values_list("id", flat=True)
        transactions = Transaction.objects.filter(
            soat_payment__id__in=soat_ids
        ).select_related("origin_account", "category").order_by("-date")
        
        return transactions
    
    @staticmethod
    def mark_alert_as_read(alert_id, user):
        """
        Marca una alerta como leída
        
        Args:
            alert_id: ID de la alerta
            user: Usuario propietario
        
        Returns:
            SOATAlert: Alerta actualizada
        
        Raises:
            ValueError: Si la alerta no existe o no pertenece al usuario
        """
        try:
            alert = SOATAlert.objects.get(id=alert_id, user=user)
            alert.is_read = True
            alert.save(update_fields=["is_read"])
            return alert
        except SOATAlert.DoesNotExist:
            raise ValueError("La alerta no existe o no te pertenece")
