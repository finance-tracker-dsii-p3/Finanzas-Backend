from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import CustomReminder, Notification
from .serializers import (
    CustomReminderListSerializer,
    CustomReminderSerializer,
    NotificationSerializer,
)
from .services import NotificationService


class NotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar notificaciones - HU-18
    Soporta notificaciones de presupuesto, facturas, SOAT, fin de mes y personalizadas
    """

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Retorna las notificaciones según el rol del usuario
        Con filtros por tipo, leídas/no leídas
        """
        queryset = Notification.objects.filter(user=self.request.user).order_by("-created_at")

        # Filtro por tipo
        notification_type = self.request.query_params.get("type")
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)

        # Filtro por leídas
        read = self.request.query_params.get("read")
        if read is not None:
            is_read = read.lower() == "true"
            queryset = queryset.filter(read=is_read)

        # Filtro por descartadas
        dismissed = self.request.query_params.get("dismissed")
        if dismissed is not None:
            is_dismissed = dismissed.lower() == "true"
            queryset = queryset.filter(is_dismissed=is_dismissed)

        # Filtro por tipo de objeto relacionado
        related_type = self.request.query_params.get("related_type")
        if related_type:
            queryset = queryset.filter(related_object_type=related_type)

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Solo admins pueden crear notificaciones
        """
        if request.user.role != "admin":
            return Response(
                {"error": "Solo administradores pueden crear notificaciones"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def mark_as_read(self, request, pk=None):
        """
        Marcar una notificación específica como leída
        """
        try:
            notification = self.get_object()

            # Verificar que la notificación pertenece al usuario actual
            if notification.user != request.user:
                return Response(
                    {"error": "No tienes permiso para modificar esta notificación"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            success = NotificationService.mark_as_read(notification.id, request.user)

            if success:
                return Response({"message": "Notificación marcada como leída"})
            return Response(
                {"error": "Error al marcar la notificación"}, status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def mark_all_read(self, request):
        """
        Marcar todas las notificaciones del usuario como leídas
        """
        try:
            notifications = Notification.objects.filter(user=request.user, read=False)
            count = notifications.count()
            notifications.update(read=True)

            return Response({"message": f"{count} notificaciones marcadas como leídas"})

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def dismiss(self, request, pk=None):
        """
        Descartar una notificación específica
        POST /api/notifications/notifications/{id}/dismiss/
        """
        try:
            notification = self.get_object()

            # Verificar que la notificación pertenece al usuario actual
            if notification.user != request.user:
                return Response(
                    {"error": "No tienes permiso para modificar esta notificación"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            notification.mark_as_dismissed()
            serializer = self.get_serializer(notification)

            return Response(
                {
                    "message": "Notificación descartada",
                    "notification": serializer.data,
                }
            )

        except Exception as e:
            # Si es DoesNotExist o cualquier otro error, retornar 404
            if "DoesNotExist" in str(type(e).__name__) or "not found" in str(e).lower():
                return Response(
                    {"error": "Notificación no encontrada"}, status=status.HTTP_404_NOT_FOUND
                )
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def dismiss_all(self, request):
        """
        Descartar todas las notificaciones no descartadas del usuario
        POST /api/notifications/notifications/dismiss_all/
        """
        try:
            notifications = Notification.objects.filter(user=request.user, is_dismissed=False)
            count = notifications.count()

            for notification in notifications:
                notification.mark_as_dismissed()

            return Response(
                {"message": f"{count} notificaciones descartadas", "updated_count": count}
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """
        Obtener resumen de notificaciones del usuario
        """
        try:
            summary = NotificationService.get_user_notifications_summary(request.user)
            serializer = self.get_serializer(summary["recent"], many=True)

            return Response(
                {
                    "total": summary["total"],
                    "unread": summary["unread"],
                    "recent": serializer.data,
                    "by_type": list(summary["by_type"]),
                }
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def system_alerts_summary(self, request):
        """
        Obtener resumen estadístico de alertas del sistema - adaptado para proyecto financiero
        Solo para administradores
        """
        if request.user.role != "admin":
            return Response(
                {"error": "Solo administradores pueden acceder a este endpoint"}, status=403
            )

        from datetime import datetime, timedelta

        # Obtener notificaciones de las últimas 30 días
        last_30_days = datetime.now() - timedelta(days=30)

        system_notifications = Notification.objects.filter(
            notification_type="system_alert", created_at__gte=last_30_days
        ).order_by("-created_at")

        # Crear resumen básico por usuario
        users_summary = {}
        for notification in system_notifications:
            username = notification.user.username
            user_name = notification.user.get_full_name()

            if username not in users_summary:
                users_summary[username] = {
                    "username": username,
                    "user_name": user_name,
                    "total_notifications": 0,
                    "last_notification": None,
                }

            users_summary[username]["total_notifications"] += 1

            if (
                not users_summary[username]["last_notification"]
                or notification.created_at > users_summary[username]["last_notification"]
            ):
                users_summary[username]["last_notification"] = notification.created_at

        return Response(
            {
                "period": "Últimos 30 días",
                "total_notifications": system_notifications.count(),
                "unique_users": len(users_summary),
                "users_summary": list(users_summary.values()),
                "recent_notifications": NotificationSerializer(
                    system_notifications[:5], many=True
                ).data,
            }
        )

    @action(detail=False, methods=["get"])
    def notifications_summary(self, request):
        """
        Obtener resumen estadístico de notificaciones - simplificado para proyecto financiero
        Solo para administradores
        """
        if request.user.role != "admin":
            return Response(
                {"error": "Solo administradores pueden acceder a este endpoint"}, status=403
            )

        from datetime import datetime, timedelta

        # Obtener notificaciones de las últimas 30 días
        last_30_days = datetime.now() - timedelta(days=30)

        recent_notifications = Notification.objects.filter(created_at__gte=last_30_days).order_by(
            "-created_at"
        )

        # Crear resumen básico por usuario
        users_summary = {}
        for notification in recent_notifications:
            username = notification.user.username
            user_name = notification.user.get_full_name()

            if username not in users_summary:
                users_summary[username] = {
                    "username": username,
                    "user_name": user_name,
                    "total_notifications": 0,
                    "unread_notifications": 0,
                    "last_notification": None,
                }

            users_summary[username]["total_notifications"] += 1
            if not notification.read:
                users_summary[username]["unread_notifications"] += 1

            if (
                not users_summary[username]["last_notification"]
                or notification.created_at > users_summary[username]["last_notification"]
            ):
                users_summary[username]["last_notification"] = notification.created_at

        return Response(
            {
                "period": "Últimos 30 días",
                "total_notifications": recent_notifications.count(),
                "unique_users": len(users_summary),
                "users_summary": list(users_summary.values()),
                "recent_notifications": NotificationSerializer(
                    recent_notifications[:5], many=True
                ).data,
            }
        )

    @action(detail=False, methods=["post"])
    def send_system_alert(self, request):
        """
        Enviar alerta del sistema a usuarios específicos
        Solo para administradores
        """
        if request.user.role != "admin":
            return Response(
                {"error": "Solo administradores pueden enviar alertas del sistema"}, status=403
            )

        try:
            title = request.data.get("title")
            message = request.data.get("message")
            user_ids = request.data.get("user_ids", None)

            if not title or not message:
                return Response({"error": "Título y mensaje son requeridos"}, status=400)

            notifications_sent = NotificationService.send_system_notification(
                title=title, message=message, user_ids=user_ids
            )

            return Response(
                {
                    "message": f"Alerta enviada a {notifications_sent} usuarios",
                    "notifications_sent": notifications_sent,
                }
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CustomReminderViewSet(viewsets.ModelViewSet):
    """
    ViewSet para recordatorios personalizados del usuario

    Endpoints:
    - list: Listar recordatorios del usuario
    - create: Crear recordatorio personalizado
    - retrieve: Ver detalle de recordatorio
    - update/partial_update: Actualizar recordatorio
    - destroy: Eliminar recordatorio
    - mark_read: Marcar recordatorio como leído
    - mark_all_read: Marcar todos como leídos
    - pending: Listar recordatorios pendientes
    - sent: Listar recordatorios enviados
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Retorna solo los recordatorios del usuario autenticado"""
        queryset = CustomReminder.objects.filter(user=self.request.user)

        # Filtro por enviados
        is_sent = self.request.query_params.get("is_sent")
        if is_sent is not None:
            queryset = queryset.filter(is_sent=is_sent.lower() == "true")

        # Filtro por leídos
        is_read = self.request.query_params.get("is_read")
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == "true")

        return queryset.order_by("reminder_date", "reminder_time")

    def get_serializer_class(self):
        """Usar serializer simplificado para list"""
        if self.action == "list":
            return CustomReminderListSerializer
        return CustomReminderSerializer

    def perform_create(self, serializer):
        """Asociar recordatorio al usuario autenticado"""
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        """
        Marca un recordatorio como leído

        POST /api/notifications/custom-reminders/{id}/mark_read/
        """
        reminder = self.get_object()
        reminder.mark_as_read()

        # También marcar la notificación asociada como leída
        if reminder.notification:
            reminder.notification.mark_as_read()

        serializer = self.get_serializer(reminder)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        """
        Marca todos los recordatorios del usuario como leídos

        POST /api/notifications/custom-reminders/mark_all_read/
        """
        reminders = self.get_queryset().filter(is_read=False)
        count = reminders.count()

        for reminder in reminders:
            reminder.mark_as_read()
            if reminder.notification:
                reminder.notification.mark_as_read()

        return Response(
            {"message": f"{count} recordatorios marcados como leídos", "updated_count": count}
        )

    @action(detail=False, methods=["get"])
    def pending(self, request):
        """
        Lista recordatorios pendientes de enviar

        GET /api/notifications/custom-reminders/pending/
        """
        reminders = self.get_queryset().filter(is_sent=False)
        serializer = CustomReminderListSerializer(reminders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def sent(self, request):
        """
        Lista recordatorios ya enviados

        GET /api/notifications/custom-reminders/sent/
        """
        reminders = self.get_queryset().filter(is_sent=True)
        serializer = CustomReminderListSerializer(reminders, many=True)
        return Response(serializer.data)
