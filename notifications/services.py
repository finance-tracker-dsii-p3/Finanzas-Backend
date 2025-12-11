import logging
from datetime import timedelta

from django.db import models
from django.utils import timezone

from users.models import User

from .models import Notification

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Servicio básico para manejar notificaciones - versión simplificada
    """

    @staticmethod
    def create_notification(user, notification_type, title, message, related_object_id=None):
        """
        Crear una notificación para un usuario
        """
        try:
            notification = Notification.objects.create(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
                related_object_id=related_object_id,
            )

            logger.info(f"Notificación creada: {notification.id} para usuario {user.username}")
            return notification

        except Exception as e:
            logger.exception(f"Error creando notificación: {e!s}")
            return None

    @staticmethod
    def mark_as_read(notification_id, user):
        """
        Marcar una notificación como leída
        """
        try:
            notification = Notification.objects.get(id=notification_id, user=user)
            notification.read = True
            notification.read_timestamp = timezone.now()
            notification.save()

            logger.info(f"Notificación {notification_id} marcada como leída")
            return True

        except Notification.DoesNotExist:
            logger.warning(
                f"Notificación {notification_id} no encontrada para usuario {user.username}"
            )
            return False
        except Exception as e:
            logger.exception(f"Error marcando notificación como leída: {e!s}")
            return False

    @staticmethod
    def mark_as_dismissed(notification_id, user):
        """
        Marcar una notificación como descartada
        """
        try:
            notification = Notification.objects.get(id=notification_id, user=user)
            notification.mark_as_dismissed()

            logger.info(f"Notificación {notification_id} marcada como descartada")
            return True

        except Notification.DoesNotExist:
            logger.warning(
                f"Notificación {notification_id} no encontrada para usuario {user.username}"
            )
            return False
        except Exception as e:
            logger.exception(f"Error marcando notificación como descartada: {e!s}")
            return False

    @staticmethod
    def get_user_notifications(user, unread_only=False, limit=None):
        """
        Obtener notificaciones de un usuario
        """
        try:
            queryset = Notification.objects.filter(user=user)

            if unread_only:
                queryset = queryset.filter(read=False)

            queryset = queryset.order_by("-created_at")

            if limit:
                queryset = queryset[:limit]

            return queryset

        except Exception as e:
            logger.exception(f"Error obteniendo notificaciones: {e!s}")
            return Notification.objects.none()

    @staticmethod
    def get_user_notifications_summary(user):
        """
        Obtener resumen de notificaciones del usuario
        """
        try:
            notifications = Notification.objects.filter(user=user)
            total = notifications.count()
            unread = notifications.filter(read=False).count()

            # Notificaciones recientes (últimas 5)
            recent = notifications.order_by("-created_at")[:5]

            # Agrupar por tipo
            from django.db.models import Count

            by_type = (
                notifications.values("notification_type")
                .annotate(count=Count("id"))
                .order_by("-count")
            )

            return {
                "total": total,
                "unread": unread,
                "recent": recent,
                "by_type": by_type,
            }

        except Exception as e:
            logger.exception(f"Error obteniendo resumen de notificaciones: {e!s}")
            return {
                "total": 0,
                "unread": 0,
                "recent": Notification.objects.none(),
                "by_type": [],
            }

    @staticmethod
    def send_system_notification(title, message, user_ids=None):
        """
        Enviar notificación del sistema a usuarios específicos o todos
        """
        try:
            if user_ids:
                users = User.objects.filter(id__in=user_ids, is_active=True)
            else:
                users = User.objects.filter(is_active=True)

            notifications_created = 0
            for user in users:
                notification = NotificationService.create_notification(
                    user=user,
                    notification_type=Notification.SYSTEM_ALERT,
                    title=title,
                    message=message,
                )
                if notification:
                    notifications_created += 1

            logger.info(f"Enviadas {notifications_created} notificaciones del sistema")
            return notifications_created

        except Exception as e:
            logger.exception(f"Error enviando notificaciones del sistema: {e!s}")
            return 0


class BasicCheckerService:
    """
    Servicio básico para verificaciones del sistema - versión simplificada
    """

    @staticmethod
    def check_unread_notifications():
        """
        Verificar usuarios con muchas notificaciones no leídas
        """
        try:
            # Usuarios con más de 10 notificaciones no leídas
            users_with_many_unread = User.objects.annotate(
                unread_count=models.Count(
                    "notifications_received", filter=models.Q(notifications_received__read=False)
                )
            ).filter(unread_count__gt=10)

            alerts = []
            for user in users_with_many_unread:
                alerts.append(
                    {
                        "user": user,
                        "unread_count": user.unread_count,
                        "severity": "warning" if user.unread_count < 20 else "critical",
                    }
                )

            return alerts

        except Exception as e:
            logger.exception(f"Error verificando notificaciones no leídas: {e!s}")
            return []

    @staticmethod
    def check_inactive_users():
        """
        Verificar usuarios inactivos por mucho tiempo
        """
        try:
            # Usuarios que no han hecho login en 30 días
            thirty_days_ago = timezone.now() - timedelta(days=30)
            inactive_users = User.objects.filter(
                is_active=True, last_login__lt=thirty_days_ago
            ) | User.objects.filter(
                is_active=True, last_login__isnull=True, date_joined__lt=thirty_days_ago
            )

            alerts = []
            for user in inactive_users:
                days_inactive = (timezone.now() - (user.last_login or user.date_joined)).days
                alerts.append(
                    {
                        "user": user,
                        "days_inactive": days_inactive,
                        "severity": "warning" if days_inactive < 60 else "critical",
                    }
                )

            return alerts

        except Exception as e:
            logger.exception(f"Error verificando usuarios inactivos: {e!s}")
            return []


# Alias para mantener compatibilidad con código existente
ExcessiveHoursChecker = BasicCheckerService
