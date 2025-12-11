"""
URLs para gestión de planes de cuotas de tarjetas de crédito
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from credit_cards.views import InstallmentPlanViewSet

router = DefaultRouter()

# /api/credit-cards/plans/ - Gestión de planes de cuotas
# GET    /api/credit-cards/plans/              - Listar planes (filtros: status, card, merchant)
# POST   /api/credit-cards/plans/              - Crear plan de cuotas
# GET    /api/credit-cards/plans/{id}/         - Ver detalle de plan
# PUT    /api/credit-cards/plans/{id}/         - Actualizar plan completo
# PATCH  /api/credit-cards/plans/{id}/         - Actualizar plan parcial
# DELETE /api/credit-cards/plans/{id}/         - Eliminar plan
# POST   /api/credit-cards/plans/{id}/pay_installment/  - Registrar pago de cuota
# GET    /api/credit-cards/plans/active/       - Listar planes activos
# GET    /api/credit-cards/plans/completed/    - Listar planes completados
router.register(r"plans", InstallmentPlanViewSet, basename="installment-plan")

urlpatterns = [
    path("", include(router.urls)),
]
