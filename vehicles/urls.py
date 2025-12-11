"""
URLs para gestión de vehículos y SOAT
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from vehicles import views

router = DefaultRouter()

# /api/vehicles/ - Gestión de vehículos
# GET    /api/vehicles/           - Listar vehículos del usuario
# POST   /api/vehicles/           - Crear vehículo
# GET    /api/vehicles/{id}/      - Ver detalle de vehículo
# PUT    /api/vehicles/{id}/      - Actualizar vehículo completo
# PATCH  /api/vehicles/{id}/      - Actualizar vehículo parcial
# DELETE /api/vehicles/{id}/      - Eliminar vehículo
# GET    /api/vehicles/{id}/soats/ - Listar SOATs de un vehículo
# GET    /api/vehicles/{id}/payment_history/ - Historial de pagos
router.register(r"vehicles", views.VehicleViewSet, basename="vehicle")

# /api/soats/ - Gestión de pólizas SOAT
# GET    /api/soats/              - Listar SOATs (filtros: status, vehicle)
# POST   /api/soats/              - Crear póliza SOAT
# GET    /api/soats/{id}/         - Ver detalle de SOAT
# PUT    /api/soats/{id}/         - Actualizar SOAT completo
# PATCH  /api/soats/{id}/         - Actualizar SOAT parcial
# DELETE /api/soats/{id}/         - Eliminar SOAT
# POST   /api/soats/{id}/register_payment/  - Registrar pago de SOAT
# POST   /api/soats/{id}/update_status/     - Actualizar estado
# GET    /api/soats/expiring_soon/  - Listar SOATs próximos a vencer
# GET    /api/soats/expired/      - Listar SOATs vencidos
router.register(r"soats", views.SOATViewSet, basename="soat")

# /api/soat-alerts/ - Gestión de alertas de vencimiento SOAT (solo lectura)
# GET  /api/soat-alerts/           - Listar alertas (filtros: is_read, alert_type, soat)
# GET  /api/soat-alerts/{id}/      - Ver detalle de alerta
# POST /api/soat-alerts/{id}/mark_read/     - Marcar alerta como leída
# POST /api/soat-alerts/mark_all_read/      - Marcar todas como leídas
router.register(r"soat-alerts", views.SOATAlertViewSet, basename="soat-alert")

urlpatterns = [
    path("", include(router.urls)),
]
