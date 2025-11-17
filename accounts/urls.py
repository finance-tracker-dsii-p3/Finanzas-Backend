"""URLs para la app accounts"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Configurar router para ViewSet
router = DefaultRouter()
router.register(r'', views.AccountViewSet, basename='account')

urlpatterns = [
    # Endpoint para opciones de cuentas (bancos, billeteras, etc.)
    # IMPORTANTE: Debe ir ANTES del router para que no sea capturado por el router
    path('options/', views.get_account_options, name='account-options'),
    # Incluir rutas del router
    path('', include(router.urls)),
]

# URLs disponibles:
# GET /api/accounts/ - Listar cuentas
# POST /api/accounts/ - Crear cuenta
# GET /api/accounts/{id}/ - Detalle de cuenta
# PUT /api/accounts/{id}/ - Actualizar cuenta completa
# PATCH /api/accounts/{id}/ - Actualizar parcialmente
# DELETE /api/accounts/{id}/ - Eliminar cuenta
# 
# Acciones adicionales:
# GET /api/accounts/summary/ - Resumen financiero del usuario
# GET /api/accounts/by_currency/?currency=COP - Filtrar cuentas por moneda
# GET /api/accounts/credit_cards_summary/ - Resumen de tarjetas de crédito
# GET /api/accounts/categories_stats/ - Estadísticas agrupadas por categoría
# POST /api/accounts/{id}/update_balance/ - Ajustar saldo manualmente
# POST /api/accounts/{id}/validate_deletion/ - Validar si se puede eliminar
# POST /api/accounts/{id}/toggle_active/ - Activar/desactivar cuenta