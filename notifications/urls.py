"""
URLs para gestión de notificaciones y recordatorios personalizados
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

# /api/notifications/notifications/ - Gestión de notificaciones del sistema
# GET    /api/notifications/notifications/              - Listar notificaciones (filtros: type, read, related_type)
# POST   /api/notifications/notifications/              - Crear notificación (solo admins)
# GET    /api/notifications/notifications/{id}/         - Ver detalle de notificación
# PUT    /api/notifications/notifications/{id}/         - Actualizar notificación
# PATCH  /api/notifications/notifications/{id}/         - Actualizar notificación parcial
# DELETE /api/notifications/notifications/{id}/         - Eliminar notificación
# POST   /api/notifications/notifications/{id}/mark_as_read/  - Marcar como leída
# POST   /api/notifications/notifications/mark_all_read/      - Marcar todas como leídas
# GET    /api/notifications/notifications/summary/      - Resumen de notificaciones
router.register(r"notifications", views.NotificationViewSet, basename="notification")

# /api/notifications/custom-reminders/ - Gestión de recordatorios personalizados
# GET    /api/notifications/custom-reminders/           - Listar recordatorios (filtros: is_sent, is_read)
# POST   /api/notifications/custom-reminders/           - Crear recordatorio personalizado
# GET    /api/notifications/custom-reminders/{id}/      - Ver detalle de recordatorio
# PUT    /api/notifications/custom-reminders/{id}/      - Actualizar recordatorio
# PATCH  /api/notifications/custom-reminders/{id}/      - Actualizar recordatorio parcial
# DELETE /api/notifications/custom-reminders/{id}/      - Eliminar recordatorio
# POST   /api/notifications/custom-reminders/{id}/mark_read/  - Marcar como leído
# POST   /api/notifications/custom-reminders/mark_all_read/   - Marcar todos como leídos
# GET    /api/notifications/custom-reminders/pending/   - Listar recordatorios pendientes
# GET    /api/notifications/custom-reminders/sent/      - Listar recordatorios enviados
router.register(r"custom-reminders", views.CustomReminderViewSet, basename="custom-reminder")

urlpatterns = [
    path("", include(router.urls)),
]
