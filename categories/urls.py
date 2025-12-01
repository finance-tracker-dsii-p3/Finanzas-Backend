"""URLs para la app categories"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Configurar router para ViewSet
router = DefaultRouter()
router.register(r"", views.CategoryViewSet, basename="category")

urlpatterns = [
    # Incluir rutas del router
    path("", include(router.urls)),
]

# URLs disponibles:
# GET /api/categories/ - Listar categorías
# POST /api/categories/ - Crear categoría
# GET /api/categories/{id}/ - Detalle de categoría
# PUT /api/categories/{id}/ - Actualizar categoría completa
# PATCH /api/categories/{id}/ - Actualizar parcialmente
# DELETE /api/categories/{id}/ - Eliminar categoría (sin datos relacionados)
#
# Acciones adicionales:
# GET /api/categories/stats/ - Estadísticas de categorías
# GET /api/categories/income/ - Solo categorías de ingresos
# GET /api/categories/expense/ - Solo categorías de gastos
# POST /api/categories/create_defaults/ - Crear categorías por defecto
# POST /api/categories/bulk_update_order/ - Actualizar orden de múltiples categorías
# POST /api/categories/{id}/delete_with_reassignment/ - Eliminar con reasignación
# POST /api/categories/{id}/toggle_active/ - Activar/desactivar categoría
# GET /api/categories/{id}/validate_deletion/ - Validar si se puede eliminar
