"""
URLs para reglas automáticas (HU-12)
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AutomaticRuleViewSet

# Configurar router para ViewSet
router = DefaultRouter()
router.register(r'', AutomaticRuleViewSet, basename='automaticRule')

urlpatterns = [
    # Incluir rutas del router
    path('', include(router.urls)),
]

# URLs disponibles:
# GET /api/rules/ - Listar reglas automáticas
# POST /api/rules/ - Crear regla automática
# GET /api/rules/{id}/ - Detalle de regla automática
# PUT /api/rules/{id}/ - Actualizar regla completa
# PATCH /api/rules/{id}/ - Actualizar parcialmente
# DELETE /api/rules/{id}/ - Eliminar regla automática
#
# Acciones adicionales:
# POST /api/rules/{id}/toggle_active/ - Activar/desactivar regla
# GET /api/rules/stats/ - Estadísticas generales de reglas
# POST /api/rules/reorder/ - Reordenar reglas por prioridad
# POST /api/rules/preview/ - Previsualizar aplicación de reglas
# GET /api/rules/active/ - Obtener solo reglas activas
# GET /api/rules/{id}/applied_transactions/ - Transacciones afectadas por regla
#
# Filtros disponibles (query parameters):
# ?active_only=true - Solo reglas activas
# ?criteria_type=description_contains - Filtrar por criterio de descripción
# ?criteria_type=transaction_type - Filtrar por criterio de tipo
# ?action_type=assign_category - Filtrar por acción de categoría
# ?action_type=assign_tag - Filtrar por acción de etiqueta
# ?search=texto - Buscar en nombre y palabra clave