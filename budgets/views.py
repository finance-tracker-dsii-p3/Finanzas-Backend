"""
Vistas para la API de presupuestos
"""

from datetime import date

from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from categories.models import Category

from .models import Budget
from .serializers import (
    BudgetCreateSerializer,
    BudgetDetailSerializer,
    BudgetListSerializer,
    BudgetStatsSerializer,
    BudgetSummarySerializer,
    BudgetUpdateSerializer,
)
from .services import BudgetService


class BudgetViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar presupuestos por categoría.

    Endpoints:
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

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filtrar presupuestos del usuario autenticado"""
        return Budget.objects.filter(user=self.request.user).select_related("category")

    def get_serializer_class(self):
        """Retornar serializer según la acción"""
        if self.action == "list":
            return BudgetListSerializer
        if self.action == "retrieve":
            return BudgetDetailSerializer
        if self.action == "create":
            return BudgetCreateSerializer
        if self.action in ["update", "partial_update"]:
            return BudgetUpdateSerializer
        return BudgetListSerializer

    def list(self, request):
        """Listar presupuestos con filtros opcionales"""
        active_only = request.query_params.get("active_only", "true").lower() == "true"
        period = request.query_params.get("period", None)

        budgets = BudgetService.get_user_budgets(
            user=request.user, active_only=active_only, period=period
        )

        if not budgets.exists():
            return Response(
                {
                    "count": 0,
                    "message": "Aún no tienes límites definidos. ¡Agrega uno para empezar a controlar tus gastos!",
                    "results": [],
                }
            )

        serializer = self.get_serializer(budgets, many=True)
        return Response({"count": budgets.count(), "results": serializer.data})

    def create(self, request):
        """Crear nuevo presupuesto"""
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        budget = serializer.save()

        # Retornar con detalle completo
        detail_serializer = BudgetDetailSerializer(budget)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Ver detalle de un presupuesto"""
        budget = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(budget)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """Actualizar presupuesto completo (PUT)"""
        budget = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(budget, data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Retornar con detalle completo
        detail_serializer = BudgetDetailSerializer(budget)
        return Response(detail_serializer.data)

    def partial_update(self, request, pk=None):
        """Actualizar presupuesto parcial (PATCH)"""
        budget = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(
            budget, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Retornar con detalle completo
        detail_serializer = BudgetDetailSerializer(budget)
        return Response(detail_serializer.data)

    def destroy(self, request, pk=None):
        """Eliminar presupuesto"""
        budget = get_object_or_404(self.get_queryset(), pk=pk)
        budget_info = BudgetService.delete_budget(budget)

        return Response(
            {
                "message": f'Presupuesto para categoría "{budget_info["category_name"]}" eliminado exitosamente.',
                "deleted_budget": budget_info,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        """Activar/Desactivar presupuesto"""
        budget = get_object_or_404(self.get_queryset(), pk=pk)
        budget = BudgetService.toggle_active(budget)

        serializer = BudgetDetailSerializer(budget)
        return Response(
            {
                "message": f"Presupuesto {'activado' if budget.is_active else 'desactivado'} exitosamente.",
                "budget": serializer.data,
            }
        )

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Obtener estadísticas generales de presupuestos"""
        stats = BudgetService.get_budget_stats(request.user)
        serializer = BudgetStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def monthly_summary(self, request):
        """Obtener resumen mensual de presupuestos con proyecciones"""
        # Permitir especificar mes/año en query params
        # TODO: Implementar cuando sea necesario
        reference_date = date.today()

        summary = BudgetService.get_monthly_summary(request.user, reference_date)
        serializer = BudgetSummarySerializer(summary, many=True)

        return Response(
            {
                "period": {"month": reference_date.month, "year": reference_date.year},
                "count": len(summary),
                "budgets": serializer.data,
            }
        )

    @action(detail=False, methods=["get"], url_path="by_category/(?P<category_id>[^/.]+)")
    def by_category(self, request, category_id=None):
        """Obtener presupuestos de una categoría específica"""
        # Verificar que la categoría exista y pertenezca al usuario
        category = get_object_or_404(Category, id=category_id, user=request.user)

        active_only = request.query_params.get("active_only", "true").lower() == "true"

        budgets = BudgetService.get_budgets_by_category(
            user=request.user, category_id=category_id, active_only=active_only
        )

        serializer = BudgetListSerializer(budgets, many=True)
        return Response(
            {
                "category": {"id": category.id, "name": category.name, "type": category.type},
                "count": budgets.count(),
                "budgets": serializer.data,
            }
        )

    @action(detail=False, methods=["get"])
    def categories_without_budget(self, request):
        """Obtener categorías de gasto sin presupuesto"""
        period = request.query_params.get("period", Budget.MONTHLY)

        categories = BudgetService.get_categories_without_budget(user=request.user, period=period)

        categories_data = [
            {"id": cat.id, "name": cat.name, "type": cat.type, "color": cat.color, "icon": cat.icon}
            for cat in categories
        ]

        return Response(
            {
                "period": period,
                "count": len(categories_data),
                "categories": categories_data,
                "message": (
                    "Estas categorías aún no tienen presupuesto asignado."
                    if categories_data
                    else "Todas tus categorías de gasto tienen presupuesto."
                ),
            }
        )

    @action(detail=False, methods=["get"])
    def alerts(self, request):
        """Obtener presupuestos que han alcanzado el umbral de alerta"""
        reference_date = date.today()

        alerts = BudgetService.get_budget_alerts(request.user, reference_date)

        alerts_data = []
        for alert in alerts:
            budget = alert["budget"]
            alerts_data.append(
                {
                    "budget_id": budget.id,
                    "category": alert["category"],
                    "category_color": budget.category.color,
                    "amount": str(budget.amount),
                    "spent_percentage": str(alert["spent_percentage"]),
                    "status": alert["status"],
                    "message": alert["message"],
                }
            )

        return Response(
            {
                "count": len(alerts_data),
                "alerts": alerts_data,
                "message": (
                    "Tienes presupuestos que requieren atención."
                    if alerts_data
                    else "Todos tus presupuestos están bajo control."
                ),
            }
        )
