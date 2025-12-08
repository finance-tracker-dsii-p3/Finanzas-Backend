"""
URLs para gestión de vehículos y SOAT
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from vehicles import views

router = DefaultRouter()

# /api/vehicles/vehicles/ - Gestión de vehículos
# GET    /api/vehicles/vehicles/           - Listar vehículos del usuario
# POST   /api/vehicles/vehicles/           - Crear vehículo
# GET    /api/vehicles/vehicles/{id}/      - Ver detalle de vehículo
# PUT    /api/vehicles/vehicles/{id}/      - Actualizar vehículo completo
# PATCH  /api/vehicles/vehicles/{id}/      - Actualizar vehículo parcial
# DELETE /api/vehicles/vehicles/{id}/      - Eliminar vehículo
router.register(r"vehicles", views.VehicleViewSet, basename="vehicle")

# /api/vehicles/soats/ - Gestión de pólizas SOAT
# GET    /api/vehicles/soats/              - Listar SOATs (filtros: status, vehicle)
# POST   /api/vehicles/soats/              - Crear póliza SOAT
# GET    /api/vehicles/soats/{id}/         - Ver detalle de SOAT
# PUT    /api/vehicles/soats/{id}/         - Actualizar SOAT completo
# PATCH  /api/vehicles/soats/{id}/         - Actualizar SOAT parcial
# DELETE /api/vehicles/soats/{id}/         - Eliminar SOAT
# POST   /api/vehicles/soats/{id}/register_payment/  - Registrar pago de SOAT
# POST   /api/vehicles/soats/{id}/update_status/     - Actualizar estado
# GET    /api/vehicles/soats/active/       - Listar SOATs activos
# GET    /api/vehicles/soats/expired/      - Listar SOATs vencidos
# GET    /api/vehicles/soats/expiring_soon/  - Listar SOATs próximos a vencer
router.register(r"soats", views.SOATViewSet, basename="soat")

# /api/vehicles/soat-alerts/ - Gestión de alertas de vencimiento SOAT (solo lectura)
# GET  /api/vehicles/soat-alerts/           - Listar alertas (filtros: is_read, alert_type, soat)
# GET  /api/vehicles/soat-alerts/{id}/      - Ver detalle de alerta
# POST /api/vehicles/soat-alerts/{id}/mark_read/     - Marcar alerta como leída
# POST /api/vehicles/soat-alerts/mark_all_read/      - Marcar todas como leídas
router.register(r"soat-alerts", views.SOATAlertViewSet, basename="soat-alert")

urlpatterns = [
    path("", include(router.urls)),
]
