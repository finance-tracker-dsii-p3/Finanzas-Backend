"""
Servicio centralizado para gestión de notificaciones
Motor de notificaciones que respeta preferencias del usuario, timezone y evita duplicados
"""

from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
from decimal import Decimal

from notifications.models import Notification, CustomReminder
from users.models import UserNotificationPreferences


class NotificationEngine:
    """
    Motor centralizado para crear y enviar notificaciones
    Respeta preferencias del usuario, timezone, evita duplicados y formatea mensajes
    """
    
    # Mensajes en español
    MESSAGES_ES = {
        "budget_warning_title": "⚠️ Alerta de Presupuesto",
        "budget_warning": "Has alcanzado el {percentage}% del presupuesto de la categoría '{category}' ({spent} de {limit}).",
        "budget_exceeded_title": "🚨 Presupuesto Excedido",
        "budget_exceeded": "Has excedido el presupuesto de la categoría '{category}' ({spent} de {limit}).",
        "bill_reminder_title": "📄 Recordatorio de Factura",
        "bill_upcoming": "La factura de {provider} vence en {days} días ({amount}).",
        "bill_due_today": "La factura de {provider} vence hoy ({amount}).",
        "bill_overdue": "La factura de {provider} está atrasada {days} días ({amount}).",
        "soat_reminder_title": "🚗 Recordatorio de SOAT",
        "soat_upcoming": "El SOAT de tu vehículo {plate} vence en {days} días.",
        "soat_due_soon": "El SOAT de tu vehículo {plate} vence pronto.",
        "soat_expired": "El SOAT de tu vehículo {plate} está vencido desde hace {days} días.",
        "month_end_title": "📅 Fin de Mes",
        "month_end": "Importa tu extracto bancario antes del cierre del mes.",
    }
    
    # Mensajes en inglés
    MESSAGES_EN = {
        "budget_warning_title": "⚠️ Budget Alert",
        "budget_warning": "You've reached {percentage}% of your '{category}' budget ({spent} of {limit}).",
        "budget_exceeded_title": "🚨 Budget Exceeded",
        "budget_exceeded": "You've exceeded your '{category}' budget ({spent} of {limit}).",
        "bill_reminder_title": "📄 Bill Reminder",
        "bill_upcoming": "{provider} bill is due in {days} days ({amount}).",
        "bill_due_today": "{provider} bill is due today ({amount}).",
        "bill_overdue": "{provider} bill is {days} days overdue ({amount}).",
        "soat_reminder_title": "🚗 SOAT Reminder",
        "soat_upcoming": "SOAT for vehicle {plate} expires in {days} days.",
        "soat_due_soon": "SOAT for vehicle {plate} expires soon.",
        "soat_expired": "SOAT for vehicle {plate} expired {days} days ago.",
        "month_end_title": "📅 Month End",
        "month_end": "Import your bank statement before the month ends.",
    }
    
    @classmethod
    def _get_user_preferences(cls, user):
        """Obtiene o crea las preferencias del usuario"""
        prefs, _ = UserNotificationPreferences.objects.get_or_create(user=user)
        return prefs
    
    @classmethod
    def _get_messages(cls, user):
        """Obtiene los mensajes en el idioma del usuario"""
        prefs = cls._get_user_preferences(user)
        return cls.MESSAGES_EN if prefs.language == "en" else cls.MESSAGES_ES
    
    @classmethod
    def _check_duplicate(cls, user, notification_type, related_id, hours=24):
        """
        Verifica si ya existe una notificación del mismo tipo en las últimas N horas
        Evita notificaciones duplicadas
        """
        cutoff = timezone.now() - timedelta(hours=hours)
        return Notification.objects.filter(
            user=user,
            notification_type=notification_type,
            related_object_id=related_id,
            created_at__gte=cutoff
        ).exists()
    
    @classmethod
    def create_budget_warning(cls, user, budget, percentage, spent, limit):
        """
        Crea notificación de alerta de presupuesto (80%)
        
        Args:
            user: Usuario propietario
            budget: Instancia de Budget
            percentage: Porcentaje alcanzado (ej: 80)
            spent: Monto gastado
            limit: Límite del presupuesto
        """
        prefs = cls._get_user_preferences(user)
        
        # Verificar si las alertas de presupuesto están habilitadas
        if not prefs.enable_budget_alerts:
            return None
        
        # Evitar duplicados
        if cls._check_duplicate(user, Notification.BUDGET_WARNING, budget.id):
            return None
        
        messages = cls._get_messages(user)
        
        # Formatear montos
        spent_str = f"${spent:,.0f}"
        limit_str = f"${limit:,.0f}"
        
        notification = Notification.objects.create(
            user=user,
            notification_type=Notification.BUDGET_WARNING,
            title=messages["budget_warning_title"],
            message=messages["budget_warning"].format(
                percentage=int(percentage),
                category=budget.category.name,
                spent=spent_str,
                limit=limit_str
            ),
            related_object_id=budget.id,
            related_object_type="budget"
        )
        
        notification.mark_as_sent()
        return notification
    
    @classmethod
    def create_budget_exceeded(cls, user, budget, spent, limit):
        """
        Crea notificación de presupuesto excedido (100%+)
        
        Args:
            user: Usuario propietario
            budget: Instancia de Budget
            spent: Monto gastado
            limit: Límite del presupuesto
        """
        prefs = cls._get_user_preferences(user)
        
        if not prefs.enable_budget_alerts:
            return None
        
        if cls._check_duplicate(user, Notification.BUDGET_EXCEEDED, budget.id):
            return None
        
        messages = cls._get_messages(user)
        
        spent_str = f"${spent:,.0f}"
        limit_str = f"${limit:,.0f}"
        
        notification = Notification.objects.create(
            user=user,
            notification_type=Notification.BUDGET_EXCEEDED,
            title=messages["budget_exceeded_title"],
            message=messages["budget_exceeded"].format(
                category=budget.category.name,
                spent=spent_str,
                limit=limit_str
            ),
            related_object_id=budget.id,
            related_object_type="budget"
        )
        
        notification.mark_as_sent()
        return notification
    
    @classmethod
    def create_bill_reminder(cls, user, bill, reminder_type, days=None):
        """
        Crea notificación de recordatorio de factura
        
        Args:
            user: Usuario propietario
            bill: Instancia de Bill
            reminder_type: "upcoming", "due_today", "overdue"
            days: Días hasta/desde vencimiento
        """
        prefs = cls._get_user_preferences(user)
        
        if not prefs.enable_bill_reminders:
            return None
        
        if cls._check_duplicate(user, Notification.BILL_REMINDER, bill.id):
            return None
        
        messages = cls._get_messages(user)
        amount_str = f"${bill.amount:,.0f}"
        
        # Determinar mensaje según tipo
        if reminder_type == "upcoming":
            message = messages["bill_upcoming"].format(
                provider=bill.provider,
                days=days,
                amount=amount_str
            )
        elif reminder_type == "due_today":
            message = messages["bill_due_today"].format(
                provider=bill.provider,
                amount=amount_str
            )
        else:  # overdue
            message = messages["bill_overdue"].format(
                provider=bill.provider,
                days=abs(days),
                amount=amount_str
            )
        
        notification = Notification.objects.create(
            user=user,
            notification_type=Notification.BILL_REMINDER,
            title=messages["bill_reminder_title"],
            message=message,
            related_object_id=bill.id,
            related_object_type="bill"
        )
        
        notification.mark_as_sent()
        return notification
    
    @classmethod
    def create_soat_reminder(cls, user, soat, alert_type, days=None):
        """
        Crea notificación de recordatorio de SOAT
        
        Args:
            user: Usuario propietario
            soat: Instancia de SOAT
            alert_type: "upcoming", "due_soon", "expired"
            days: Días hasta/desde vencimiento
        """
        prefs = cls._get_user_preferences(user)
        
        if not prefs.enable_soat_reminders:
            return None
        
        if cls._check_duplicate(user, Notification.SOAT_REMINDER, soat.id):
            return None
        
        messages = cls._get_messages(user)
        plate = soat.vehicle.plate
        
        # Determinar mensaje según tipo
        if alert_type == "upcoming":
            message = messages["soat_upcoming"].format(plate=plate, days=days)
        elif alert_type == "due_soon":
            message = messages["soat_due_soon"].format(plate=plate)
        else:  # expired
            message = messages["soat_expired"].format(plate=plate, days=abs(days))
        
        notification = Notification.objects.create(
            user=user,
            notification_type=Notification.SOAT_REMINDER,
            title=messages["soat_reminder_title"],
            message=message,
            related_object_id=soat.id,
            related_object_type="soat"
        )
        
        notification.mark_as_sent()
        return notification
    
    @classmethod
    def create_month_end_reminder(cls, user):
        """
        Crea notificación de recordatorio de fin de mes
        
        Args:
            user: Usuario propietario
        """
        prefs = cls._get_user_preferences(user)
        
        if not prefs.enable_month_end_reminders:
            return None
        
        # Evitar duplicados en el mes actual
        now = timezone.now()
        if Notification.objects.filter(
            user=user,
            notification_type=Notification.MONTH_END_REMINDER,
            created_at__year=now.year,
            created_at__month=now.month
        ).exists():
            return None
        
        messages = cls._get_messages(user)
        
        notification = Notification.objects.create(
            user=user,
            notification_type=Notification.MONTH_END_REMINDER,
            title=messages["month_end_title"],
            message=messages["month_end"],
            related_object_type="system"
        )
        
        notification.mark_as_sent()
        return notification
    
    @classmethod
    def create_custom_reminder_notification(cls, custom_reminder):
        """
        Crea notificación para un recordatorio personalizado
        
        Args:
            custom_reminder: Instancia de CustomReminder
        """
        prefs = cls._get_user_preferences(custom_reminder.user)
        
        if not prefs.enable_custom_reminders:
            return None
        
        # Crear notificación
        notification = Notification.objects.create(
            user=custom_reminder.user,
            notification_type=Notification.CUSTOM_REMINDER,
            title=custom_reminder.title,
            message=custom_reminder.message,
            related_object_id=custom_reminder.id,
            related_object_type="custom_reminder"
        )
        
        # Vincular con el recordatorio y marcar como enviado
        custom_reminder.notification = notification
        custom_reminder.is_sent = True
        custom_reminder.sent_at = timezone.now()
        custom_reminder.save(update_fields=["notification", "is_sent", "sent_at"])
        
        notification.mark_as_sent()
        return notification
    
    @classmethod
    def get_pending_custom_reminders(cls):
        """
        Obtiene recordatorios personalizados pendientes de enviar
        Considera el timezone del usuario
        """
        now = timezone.now()
        
        # Obtener recordatorios no enviados cuya fecha/hora ya pasó
        pending_reminders = []
        
        for reminder in CustomReminder.objects.filter(is_sent=False).select_related('user'):
            try:
                # Obtener timezone del usuario
                prefs = cls._get_user_preferences(reminder.user)
                user_tz = prefs.timezone_object
                
                # Convertir fecha/hora del recordatorio al timezone del usuario
                reminder_datetime = timezone.make_aware(
                    datetime.combine(reminder.reminder_date, reminder.reminder_time),
                    user_tz
                )
                
                # Verificar si ya es hora de enviar
                if now >= reminder_datetime:
                    pending_reminders.append(reminder)
            except Exception as e:
                # Si hay error, usar lógica simple
                reminder_date = datetime.combine(reminder.reminder_date, reminder.reminder_time)
                if now.date() >= reminder.reminder_date:
                    pending_reminders.append(reminder)
        
        return pending_reminders
    
    @classmethod
    def check_month_end_reminders(cls):
        """
        Verifica si es día 28 del mes y envía recordatorios de fin de mes
        """
        now = timezone.now()
        
        # Solo enviar el día 28 a las 9 AM
        if now.day != 28:
            return []
        
        # Obtener usuarios con preferencias habilitadas
        notifications_created = []
        
        prefs_list = UserNotificationPreferences.objects.filter(
            enable_month_end_reminders=True
        ).select_related('user')
        
        for prefs in prefs_list:
            # Verificar timezone del usuario para enviar a las 9 AM de su zona
            user_tz = prefs.timezone_object
            user_now = now.astimezone(user_tz)
            
            # Solo enviar entre las 8 y 10 AM
            if 8 <= user_now.hour < 10:
                notification = cls.create_month_end_reminder(prefs.user)
                if notification:
                    notifications_created.append(notification)
        
        return notifications_created
