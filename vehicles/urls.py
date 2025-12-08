"""
URLs para gestión de vehículos y SOAT
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from vehicles import views

router = DefaultRouter()
router.register(r"vehicles", views.VehicleViewSet, basename="vehicle")
router.register(r"soats", views.SOATViewSet, basename="soat")
router.register(r"soat-alerts", views.SOATAlertViewSet, basename="soat-alert")

urlpatterns = [
    path("", include(router.urls)),
]
