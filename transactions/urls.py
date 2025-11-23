"""URLs para la app transactions"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Configurar router para ViewSet
router = DefaultRouter()
router.register(r"", views.TransactionViewSet, basename="transaction")

urlpatterns = [
    # Incluir rutas del router
    path("", include(router.urls)),
]

# URLs disponibles:
# GET /api/transactions/ - Listar transacciones
# POST /api/transactions/ - Crear transacción (con aplicación automática de reglas HU-12)
# GET /api/transactions/{id}/ - Detalle de transacción
# PUT /api/transactions/{id}/ - Actualizar transacción completa
# PATCH /api/transactions/{id}/ - Actualizar parcialmente
# DELETE /api/transactions/{id}/ - Eliminar transacción
#
# Filtros disponibles (query parameters):
# ?type=1 - Filtrar por tipo (1=Income, 2=Expense, 3=Transfer, 4=Saving)
# ?category={id} - Filtrar por categoría (HU-12)
# ?applied_rule={id} - Filtrar por regla aplicada (HU-12)
# ?date_from=YYYY-MM-DD - Desde fecha
# ?date_to=YYYY-MM-DD - Hasta fecha
# ?min_amount=1000 - Monto mínimo
# ?max_amount=50000 - Monto máximo
# ?search=texto - Buscar en descripción (HU-12)
# ?ordering=date,-total_amount - Ordenar por campos
