from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),  # CRUD de notificaciones
    # Rutas del ViewSet generadas automáticamente:
    # GET /notifications/ - Listar notificaciones
    # POST /notifications/ - Crear notificación (solo admins)
    # GET /notifications/{id}/ - Detalle de notificación
    # PUT/PATCH /notifications/{id}/ - Actualizar notificación
    # DELETE /notifications/{id}/ - Eliminar notificación (solo admins)
    # GET /notifications/summary/ - Resumen de notificaciones del usuario
    # GET /notifications/system_alerts_summary/ - Resumen de alertas del sistema (solo admins)
    # GET /notifications/notifications_summary/ - Resumen estadístico (solo admins)
]