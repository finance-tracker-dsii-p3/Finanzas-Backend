from django.utils import timezone
from datetime import timedelta
from users.models import User
from notifications.models import Notification
from credit_cards.services import InstallmentPlanService
from credit_cards.models import InstallmentPlan
import logging

logger = logging.getLogger(__name__)


class DashboardService:
    """
    Servicio para generar datos del dashboard - adaptado para proyecto financiero
    """

    @staticmethod
    def get_admin_dashboard_data(user):
        """
        Dashboard básico para administradores - se expandirá para el proyecto financiero
        """
        try:
            # Estadísticas básicas de usuarios
            total_users = User.objects.count()
            active_users = User.objects.filter(is_verified=True, is_active=True).count()
            pending_verifications = User.objects.filter(is_verified=False).count()

            # Estadísticas de notificaciones
            unread_notifications = Notification.objects.filter(user=user, read=False).count()
            recent_notifications = Notification.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count()

            # Mini cards básicas
            mini_cards = [
                {
                    "title": "Total Usuarios",
                    "value": str(total_users),
                    "icon": "👥",
                    "color": "blue",
                    "trend": "stable",
                    "trend_value": str(total_users),
                },
                {
                    "title": "Usuarios Activos",
                    "value": str(active_users),
                    "icon": "✅",
                    "color": "green",
                    "trend": "stable",
                    "trend_value": str(active_users),
                },
                {
                    "title": "Pendientes Verificación",
                    "value": str(pending_verifications),
                    "icon": "⏳",
                    "color": "orange",
                    "trend": "stable",
                    "trend_value": str(pending_verifications),
                },
                {
                    "title": "Notificaciones (7d)",
                    "value": str(recent_notifications),
                    "icon": "🔔",
                    "color": "purple",
                    "trend": "stable",
                    "trend_value": str(recent_notifications),
                },
            ]

            return {
                "user_info": {
                    "id": user.id,
                    "username": user.username,
                    "full_name": user.get_full_name(),
                    "role": user.role,
                    "is_verified": user.is_verified,
                },
                "stats": {
                    "total_users": total_users,
                    "active_users": active_users,
                    "pending_verifications": pending_verifications,
                    "unread_notifications": unread_notifications,
                    "recent_notifications": recent_notifications,
                },
                "mini_cards": mini_cards,
                "recent_activities": DashboardService._get_recent_activities(),
                "alerts": DashboardService._get_alerts(),
                "charts_data": {"basic_stats": True},
            }

        except Exception as e:
            logger.error(f"Error generando dashboard de admin: {e}")
            return DashboardService._get_error_dashboard()

    @staticmethod
    def get_user_dashboard_data(user):
        """
        Dashboard básico para usuarios - se expandirá para el proyecto financiero
        """
        try:
            # Notificaciones del usuario
            unread_notifications = Notification.objects.filter(user=user, read=False).count()
            total_notifications = Notification.objects.filter(user=user).count()

            # Información de planes de cuotas (HU-16)
            today = timezone.now().date()
            upcoming_payments_qs = InstallmentPlanService.get_upcoming_payments(user, days=30)[:5]
            upcoming_payments = [
                {
                    "plan_id": p.plan_id,
                    "installment_number": p.installment_number,
                    "due_date": p.due_date,
                    "installment_amount": p.installment_amount,
                    "status": p.status,
                    "credit_card": p.plan.credit_card_account.name,
                }
                for p in upcoming_payments_qs
            ]

            monthly_summary = InstallmentPlanService.get_monthly_summary(
                user, today.year, today.month
            )

            active_plans = InstallmentPlan.objects.filter(user=user, status="active").count()

            # Mini cards para usuarios
            mini_cards = [
                {
                    "title": "Estado de Cuenta",
                    "value": "Activo" if user.is_verified else "Pendiente",
                    "icon": "✅" if user.is_verified else "⏳",
                    "color": "green" if user.is_verified else "orange",
                },
                {
                    "title": "Notificaciones",
                    "value": str(unread_notifications),
                    "icon": "🔔",
                    "color": "red" if unread_notifications > 0 else "green",
                    "trend": "stable",
                    "trend_value": f"{unread_notifications} no leídas",
                },
                {
                    "title": "Total Notificaciones",
                    "value": str(total_notifications),
                    "icon": "📊",
                    "color": "blue",
                    "trend": "stable",
                    "trend_value": f"{total_notifications} total",
                },
                {
                    "title": "Perfil",
                    "value": "Completo" if user.first_name and user.last_name else "Incompleto",
                    "icon": "👤",
                    "color": "green" if user.first_name and user.last_name else "orange",
                },
            ]

            return {
                "user_info": {
                    "id": user.id,
                    "username": user.username,
                    "full_name": user.get_full_name(),
                    "role": user.role,
                    "is_verified": user.is_verified,
                },
                "stats": {
                    "unread_notifications": unread_notifications,
                    "total_notifications": total_notifications,
                    "profile_complete": bool(user.first_name and user.last_name),
                },
                "mini_cards": mini_cards,
                "recent_activities": DashboardService._get_user_recent_activities(user),
                "alerts": DashboardService._get_user_alerts(user),
                "charts_data": {"basic_stats": True},
                "credit_cards": {
                    "upcoming_payments": upcoming_payments,
                    "monthly_summary": monthly_summary,
                    "active_plans": active_plans,
                },
            }

        except Exception as e:
            logger.error(f"Error generando dashboard de usuario: {e}")
            return DashboardService._get_error_dashboard()

    @staticmethod
    def _get_recent_activities():
        """
        Actividades recientes básicas del sistema
        """
        try:
            # Últimas notificaciones del sistema como actividades
            recent_notifications = Notification.objects.select_related("user").order_by(
                "-created_at"
            )[:10]

            activities = []
            for notification in recent_notifications:
                activities.append(
                    {
                        "id": notification.id,
                        "type": "notification",
                        "user": notification.user.get_full_name(),
                        "timestamp": notification.created_at,
                        "description": f"Notificación: {notification.title}",
                    }
                )

            return activities

        except Exception as e:
            logger.error(f"Error obteniendo actividades recientes: {e}")
            return []

    @staticmethod
    def _get_user_recent_activities(user):
        """
        Actividades recientes del usuario
        """
        try:
            user_notifications = Notification.objects.filter(user=user).order_by("-created_at")[:5]

            activities = []
            for notification in user_notifications:
                activities.append(
                    {
                        "id": notification.id,
                        "type": "notification",
                        "timestamp": notification.created_at,
                        "description": f"Recibiste: {notification.title}",
                        "read": notification.read,
                    }
                )

            return activities

        except Exception as e:
            logger.error(f"Error obteniendo actividades del usuario: {e}")
            return []

    @staticmethod
    def _get_alerts():
        """
        Alertas básicas del sistema
        """
        try:
            alerts = []

            # Usuarios pendientes de verificación
            pending_count = User.objects.filter(is_verified=False, is_active=True).count()
            if pending_count > 0:
                alerts.append(
                    {
                        "type": "pending_users",
                        "severity": "warning",
                        "title": "Usuarios pendientes de verificación",
                        "message": f"Hay {pending_count} usuarios esperando verificación",
                        "timestamp": timezone.now(),
                    }
                )

            return alerts

        except Exception as e:
            logger.error(f"Error obteniendo alertas: {e}")
            return []

    @staticmethod
    def _get_user_alerts(user):
        """
        Alertas del usuario
        """
        try:
            alerts = []

            # Verificación pendiente
            if not user.is_verified:
                alerts.append(
                    {
                        "type": "verification_pending",
                        "severity": "info",
                        "title": "Verificación pendiente",
                        "message": "Tu cuenta está pendiente de verificación por un administrador",
                        "timestamp": timezone.now(),
                    }
                )

            # Perfil incompleto
            if not (user.first_name and user.last_name):
                alerts.append(
                    {
                        "type": "profile_incomplete",
                        "severity": "warning",
                        "title": "Completa tu perfil",
                        "message": "Agrega tu nombre y apellidos para completar tu perfil",
                        "timestamp": timezone.now(),
                    }
                )

            return alerts

        except Exception as e:
            logger.error(f"Error obteniendo alertas del usuario: {e}")
            return []

    @staticmethod
    def _get_error_dashboard():
        """
        Dashboard de error por defecto
        """
        return {
            "user_info": {},
            "stats": {},
            "mini_cards": [],
            "recent_activities": [],
            "alerts": [],
            "charts_data": {"basic_stats": True},
        }
