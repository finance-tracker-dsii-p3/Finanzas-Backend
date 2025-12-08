from rest_framework.routers import DefaultRouter
from credit_cards.views import InstallmentPlanViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r"plans", InstallmentPlanViewSet, basename="installment-plan")

urlpatterns = [
    path("", include(router.urls)),
]
