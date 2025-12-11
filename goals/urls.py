"""URLs para la app categories"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

# Configurar router para ViewSet
router = DefaultRouter()
router.register(r"", views.GoalViewSet, basename="goal")

urlpatterns = [
    # Incluir rutas del router
    path("", include(router.urls)),
]
