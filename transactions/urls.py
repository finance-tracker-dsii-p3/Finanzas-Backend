"""URLs para la app transactions"""

from django.urls import include, path
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
# ?category={id} - Filtrar por categoría (HU-10)
# ?origin_account={id} - Filtrar por cuenta origen
# ?destination_account={id} - Filtrar por cuenta destino
# ?start_date=YYYY-MM-DD - Desde fecha
# ?end_date=YYYY-MM-DD - Hasta fecha
# ?search=texto - Buscar en tag, description, note y nombre de categoría (HU-10)
# ?ordering=date,-total_amount - Ordenar por campos
#
# Acciones adicionales:
# POST /api/transactions/bulk_delete/ - Eliminar múltiples transacciones (HU-10)
# Body: {"ids": [1, 2, 3, ...]}
