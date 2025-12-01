"""
Servicios de lógica de negocio para presupuestos
"""

from decimal import Decimal
from datetime import date
from django.db.models import Sum
from .models import Budget
from categories.models import Category
import logging

logger = logging.getLogger(__name__)


class BudgetService:
    """Servicio para gestionar presupuestos"""

    @staticmethod
    def get_user_budgets(user, active_only=True, period=None):
        """
        Obtener presupuestos del usuario.

        Args:
            user: Usuario propietario
            active_only: Si True, solo presupuestos activos
            period: Filtrar por período ('monthly', 'yearly')

        Returns:
            QuerySet: Presupuestos filtrados
        """
        queryset = Budget.objects.filter(user=user).select_related("category")

        if active_only:
            queryset = queryset.filter(is_active=True)

        if period:
            queryset = queryset.filter(period=period)

        return queryset.order_by("-created_at")

    @staticmethod
    def get_budgets_by_category(user, category_id, active_only=True):
        """
        Obtener presupuestos de una categoría específica.

        Args:
            user: Usuario propietario
            category_id: ID de la categoría
            active_only: Si True, solo presupuestos activos

        Returns:
            QuerySet: Presupuestos de la categoría
        """
        queryset = Budget.objects.filter(user=user, category_id=category_id).select_related(
            "category"
        )

        if active_only:
            queryset = queryset.filter(is_active=True)

        return queryset.order_by("-created_at")

    @staticmethod
    def get_budget_stats(user):
        """
        Obtener estadísticas generales de presupuestos del usuario.

        Args:
            user: Usuario propietario

        Returns:
            dict: Estadísticas de presupuestos
        """
        budgets = Budget.objects.filter(user=user)
        active_budgets = budgets.filter(is_active=True)

        # Contadores por estado
        exceeded_count = 0
        warning_count = 0
        good_count = 0
        total_spent = Decimal("0.00")

        for budget in active_budgets:
            status = budget.get_status()
            if status == "exceeded":
                exceeded_count += 1
            elif status == "warning":
                warning_count += 1
            else:
                good_count += 1

            total_spent += budget.get_spent_amount()

        # Totales
        total_allocated = active_budgets.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        total_remaining = total_allocated - total_spent

        # Porcentaje promedio de uso
        avg_percentage = Decimal("0.00")
        if active_budgets.exists():
            percentages = [b.get_spent_percentage() for b in active_budgets]
            if percentages:
                avg_percentage = sum(percentages) / len(percentages)

        return {
            "total_budgets": budgets.count(),
            "active_budgets": active_budgets.count(),
            "exceeded_budgets": exceeded_count,
            "warning_budgets": warning_count,
            "good_budgets": good_count,
            "total_allocated": total_allocated,
            "total_spent": total_spent,
            "total_remaining": total_remaining,
            "average_usage_percentage": round(avg_percentage, 2),
            "monthly_budgets_count": budgets.filter(period=Budget.MONTHLY).count(),
            "yearly_budgets_count": budgets.filter(period=Budget.YEARLY).count(),
        }

    @staticmethod
    def get_monthly_summary(user, reference_date=None):
        """
        Obtener resumen de presupuestos mensuales con proyecciones.

        Args:
            user: Usuario propietario
            reference_date: Fecha de referencia (default: hoy)

        Returns:
            list: Lista de resúmenes por categoría
        """
        if reference_date is None:
            reference_date = date.today()

        budgets = Budget.objects.filter(
            user=user, period=Budget.MONTHLY, is_active=True
        ).select_related("category")

        summary = []
        for budget in budgets:
            projection = budget.get_projection(reference_date)

            summary.append(
                {
                    "budget_id": budget.id,
                    "category_id": budget.category.id,
                    "category_name": budget.category.name,
                    "category_color": budget.category.color,
                    "category_icon": budget.category.icon,
                    "amount": budget.amount,
                    "spent_amount": budget.get_spent_amount(reference_date),
                    "spent_percentage": budget.get_spent_percentage(reference_date),
                    "remaining_amount": budget.get_remaining_amount(reference_date),
                    "status": budget.get_status(reference_date),
                    "projection": projection,
                }
            )

        # Ordenar por porcentaje gastado (mayor a menor)
        summary.sort(key=lambda x: x["spent_percentage"], reverse=True)

        return summary

    @staticmethod
    def create_budget(
        user,
        category,
        amount,
        calculation_mode=Budget.BASE,
        period=Budget.MONTHLY,
        start_date=None,
        is_active=True,
        alert_threshold=Decimal("80.00"),
    ):
        """
        Crear un nuevo presupuesto.

        Args:
            user: Usuario propietario
            category: Categoría del presupuesto
            amount: Monto límite
            calculation_mode: 'base' o 'total'
            period: 'monthly' o 'yearly'
            start_date: Fecha de inicio (default: hoy)
            is_active: Si está activo
            alert_threshold: Umbral de alerta en porcentaje

        Returns:
            Budget: Presupuesto creado

        Raises:
            ValueError: Si la categoría no pertenece al usuario o ya existe presupuesto
        """
        # Validar que la categoría pertenezca al usuario
        if category.user != user:
            raise ValueError("La categoría no pertenece al usuario.")

        # Validar que no exista presupuesto para esta categoría y período
        if Budget.objects.filter(user=user, category=category, period=period).exists():
            raise ValueError(
                f"Ya existe un presupuesto {Budget(period=period).get_period_display().lower()} "
                f"para la categoría {category.name}."
            )

        # Validar que la categoría sea de tipo gasto
        if category.type != Category.EXPENSE:
            raise ValueError("Solo se pueden crear presupuestos para categorías de gasto.")

        if start_date is None:
            start_date = date.today()

        budget = Budget.objects.create(
            user=user,
            category=category,
            amount=amount,
            calculation_mode=calculation_mode,
            period=period,
            start_date=start_date,
            is_active=is_active,
            alert_threshold=alert_threshold,
        )

        logger.info(
            f"Presupuesto creado: {budget.id} - Usuario: {user.id} - "
            f"Categoría: {category.name} - Monto: {amount}"
        )

        return budget

    @staticmethod
    def update_budget(budget, **kwargs):
        """
        Actualizar un presupuesto existente.

        Args:
            budget: Instancia del presupuesto
            **kwargs: Campos a actualizar

        Returns:
            Budget: Presupuesto actualizado
        """
        for key, value in kwargs.items():
            if hasattr(budget, key):
                setattr(budget, key, value)

        budget.save()

        logger.info(f"Presupuesto actualizado: {budget.id} - Usuario: {budget.user.id}")

        return budget

    @staticmethod
    def delete_budget(budget):
        """
        Eliminar un presupuesto.

        Args:
            budget: Instancia del presupuesto

        Returns:
            dict: Información del presupuesto eliminado
        """
        budget_info = {
            "id": budget.id,
            "category_name": budget.category.name,
            "amount": budget.amount,
        }

        budget.delete()

        logger.info(
            f"Presupuesto eliminado: {budget_info['id']} - "
            f"Categoría: {budget_info['category_name']}"
        )

        return budget_info

    @staticmethod
    def toggle_active(budget):
        """
        Alternar estado activo/inactivo del presupuesto.

        Args:
            budget: Instancia del presupuesto

        Returns:
            Budget: Presupuesto actualizado
        """
        budget.is_active = not budget.is_active
        budget.save()

        logger.info(f"Presupuesto {'activado' if budget.is_active else 'desactivado'}: {budget.id}")

        return budget

    @staticmethod
    def get_categories_without_budget(user, period=Budget.MONTHLY):
        """
        Obtener categorías de gasto del usuario que no tienen presupuesto.

        Args:
            user: Usuario propietario
            period: Período del presupuesto ('monthly' o 'yearly')

        Returns:
            QuerySet: Categorías sin presupuesto
        """
        # Obtener IDs de categorías que ya tienen presupuesto
        budgeted_category_ids = Budget.objects.filter(user=user, period=period).values_list(
            "category_id", flat=True
        )

        # Obtener categorías de gasto sin presupuesto
        categories_without_budget = Category.objects.filter(
            user=user, type=Category.EXPENSE, is_active=True
        ).exclude(id__in=budgeted_category_ids)

        return categories_without_budget

    @staticmethod
    def get_budget_alerts(user, reference_date=None):
        """
        Obtener presupuestos que han alcanzado el umbral de alerta.

        Args:
            user: Usuario propietario
            reference_date: Fecha de referencia (default: hoy)

        Returns:
            list: Lista de presupuestos con alertas
        """
        budgets = Budget.objects.filter(user=user, is_active=True).select_related("category")

        alerts = []
        for budget in budgets:
            if budget.is_alert_triggered(reference_date):
                alerts.append(
                    {
                        "budget": budget,
                        "category": budget.category.name,
                        "spent_percentage": budget.get_spent_percentage(reference_date),
                        "status": budget.get_status(reference_date),
                        "message": budget.get_status_display_text(reference_date),
                    }
                )

        return alerts
