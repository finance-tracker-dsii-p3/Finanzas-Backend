"""URLs para la app categories"""

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
