"""
URLs para la API de presupuestos
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BudgetViewSet

# Router para el ViewSet
router = DefaultRouter()
router.register(r'', BudgetViewSet, basename='budget')

urlpatterns = [
    path('', include(router.urls)),
]

""" 
    urls disponibles:
    
    - GET /budgets/ - Listar presupuestos
    - POST /budgets/ - Crear presupuesto
    - GET /budgets/{id}/ - Ver detalle
    - PATCH /budgets/{id}/ - Actualizar
    - DELETE /budgets/{id}/ - Eliminar
    - POST /budgets/{id}/toggle_active/ - Activar/Desactivar
    - GET /budgets/stats/ - Estadísticas generales
    - GET /budgets/monthly_summary/ - Resumen mensual
    - GET /budgets/by_category/{category_id}/ - Por categoría
    - GET /budgets/categories_without_budget/ - Categorías sin presupuesto
    - GET /budgets/alerts/ - Presupuestos con alertas
    """