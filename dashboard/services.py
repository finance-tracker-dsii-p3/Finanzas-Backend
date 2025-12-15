import logging
from datetime import timedelta

from django.utils import timezone

from credit_cards.models import InstallmentPlan
from credit_cards.services import InstallmentPlanService
from notifications.models import Notification
from users.models import User

logger = logging.getLogger(__name__)


class DashboardService:
    """
    Servicio para generar datos del dashboard - adaptado para proyecto financiero
    """

    @staticmethod
    def get_admin_dashboard_data(user):
        """
        Dashboard básico para administradores - se expandirá para el proyecto financiero
        """
        try:
            # Estadísticas básicas de usuarios
            total_users = User.objects.count()
            active_users = User.objects.filter(is_verified=True, is_active=True).count()
            pending_verifications = User.objects.filter(is_verified=False).count()

            # Estadísticas de notificaciones
            unread_notifications = Notification.objects.filter(user=user, read=False).count()
            recent_notifications = Notification.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count()

            # Mini cards básicas
            mini_cards = [
                {
                    "title": "Total Usuarios",
                    "value": str(total_users),
                    "icon": "👥",
                    "color": "blue",
                    "trend": "stable",
                    "trend_value": str(total_users),
                },
                {
                    "title": "Usuarios Activos",
                    "value": str(active_users),
                    "icon": "✅",
                    "color": "green",
                    "trend": "stable",
                    "trend_value": str(active_users),
                },
                {
                    "title": "Pendientes Verificación",
                    "value": str(pending_verifications),
                    "icon": "⏳",
                    "color": "orange",
                    "trend": "stable",
                    "trend_value": str(pending_verifications),
                },
                {
                    "title": "Notificaciones (7d)",
                    "value": str(recent_notifications),
                    "icon": "🔔",
                    "color": "purple",
                    "trend": "stable",
                    "trend_value": str(recent_notifications),
                },
            ]

            return {
                "user_info": {
                    "id": user.id,
                    "username": user.username,
                    "full_name": user.get_full_name(),
                    "role": user.role,
                    "is_verified": user.is_verified,
                },
                "stats": {
                    "total_users": total_users,
                    "active_users": active_users,
                    "pending_verifications": pending_verifications,
                    "unread_notifications": unread_notifications,
                    "recent_notifications": recent_notifications,
                },
                "mini_cards": mini_cards,
                "recent_activities": DashboardService._get_recent_activities(),
                "alerts": DashboardService._get_alerts(),
                "charts_data": {"basic_stats": True},
            }

        except Exception as e:
            logger.exception(f"Error generando dashboard de admin: {e}")
            return DashboardService._get_error_dashboard()

    @staticmethod
    def get_user_dashboard_data(user):
        """
        Dashboard básico para usuarios - se expandirá para el proyecto financiero
        """
        try:
            # Notificaciones del usuario
            unread_notifications = Notification.objects.filter(user=user, read=False).count()
            total_notifications = Notification.objects.filter(user=user).count()

            # Información de planes de cuotas (HU-16)
            today = timezone.now().date()
            upcoming_payments_qs = InstallmentPlanService.get_upcoming_payments(user, days=30)[:5]
            upcoming_payments = [
                {
                    "plan_id": p.plan_id,
                    "installment_number": p.installment_number,
                    "due_date": p.due_date,
                    "installment_amount": p.installment_amount,
                    "status": p.status,
                    "credit_card": p.plan.credit_card_account.name,
                }
                for p in upcoming_payments_qs
            ]

            monthly_summary = InstallmentPlanService.get_monthly_summary(
                user, today.year, today.month
            )

            active_plans = InstallmentPlan.objects.filter(user=user, status="active").count()

            # Mini cards para usuarios
            mini_cards = [
                {
                    "title": "Estado de Cuenta",
                    "value": "Activo" if user.is_verified else "Pendiente",
                    "icon": "✅" if user.is_verified else "⏳",
                    "color": "green" if user.is_verified else "orange",
                },
                {
                    "title": "Notificaciones",
                    "value": str(unread_notifications),
                    "icon": "🔔",
                    "color": "red" if unread_notifications > 0 else "green",
                    "trend": "stable",
                    "trend_value": f"{unread_notifications} no leídas",
                },
                {
                    "title": "Total Notificaciones",
                    "value": str(total_notifications),
                    "icon": "📊",
                    "color": "blue",
                    "trend": "stable",
                    "trend_value": f"{total_notifications} total",
                },
                {
                    "title": "Perfil",
                    "value": "Completo" if user.first_name and user.last_name else "Incompleto",
                    "icon": "👤",
                    "color": "green" if user.first_name and user.last_name else "orange",
                },
            ]

            return {
                "user_info": {
                    "id": user.id,
                    "username": user.username,
                    "full_name": user.get_full_name(),
                    "role": user.role,
                    "is_verified": user.is_verified,
                },
                "stats": {
                    "unread_notifications": unread_notifications,
                    "total_notifications": total_notifications,
                    "profile_complete": bool(user.first_name and user.last_name),
                },
                "mini_cards": mini_cards,
                "recent_activities": DashboardService._get_user_recent_activities(user),
                "alerts": DashboardService._get_user_alerts(user),
                "charts_data": {"basic_stats": True},
                "credit_cards": {
                    "upcoming_payments": upcoming_payments,
                    "monthly_summary": monthly_summary,
                    "active_plans": active_plans,
                },
            }

        except Exception as e:
            logger.exception(f"Error generando dashboard de usuario: {e}")
            return DashboardService._get_error_dashboard()

    @staticmethod
    def _get_recent_activities():
        """
        Actividades recientes básicas del sistema
        """
        try:
            # Últimas notificaciones del sistema como actividades
            recent_notifications = Notification.objects.select_related("user").order_by(
                "-created_at"
            )[:10]

            activities = []
            for notification in recent_notifications:
                activities.append(
                    {
                        "id": notification.id,
                        "type": "notification",
                        "user": notification.user.get_full_name(),
                        "timestamp": notification.created_at,
                        "description": f"Notificación: {notification.title}",
                    }
                )

            return activities

        except Exception as e:
            logger.exception(f"Error obteniendo actividades recientes: {e}")
            return []

    @staticmethod
    def _get_user_recent_activities(user):
        """
        Actividades recientes del usuario
        """
        try:
            user_notifications = Notification.objects.filter(user=user).order_by("-created_at")[:5]

            activities = []
            for notification in user_notifications:
                activities.append(
                    {
                        "id": notification.id,
                        "type": "notification",
                        "timestamp": notification.created_at,
                        "description": f"Recibiste: {notification.title}",
                        "read": notification.read,
                    }
                )

            return activities

        except Exception as e:
            logger.exception(f"Error obteniendo actividades del usuario: {e}")
            return []

    @staticmethod
    def _get_alerts():
        """
        Alertas básicas del sistema
        """
        try:
            alerts = []

            # Usuarios pendientes de verificación
            pending_count = User.objects.filter(is_verified=False, is_active=True).count()
            if pending_count > 0:
                alerts.append(
                    {
                        "type": "pending_users",
                        "severity": "warning",
                        "title": "Usuarios pendientes de verificación",
                        "message": f"Hay {pending_count} usuarios esperando verificación",
                        "timestamp": timezone.now(),
                    }
                )

            return alerts

        except Exception as e:
            logger.exception(f"Error obteniendo alertas: {e}")
            return []

    @staticmethod
    def _get_user_alerts(user):
        """
        Alertas del usuario
        """
        try:
            alerts = []

            # Verificación pendiente
            if not user.is_verified:
                alerts.append(
                    {
                        "type": "verification_pending",
                        "severity": "info",
                        "title": "Verificación pendiente",
                        "message": "Tu cuenta está pendiente de verificación por un administrador",
                        "timestamp": timezone.now(),
                    }
                )

            # Perfil incompleto
            if not (user.first_name and user.last_name):
                alerts.append(
                    {
                        "type": "profile_incomplete",
                        "severity": "warning",
                        "title": "Completa tu perfil",
                        "message": "Agrega tu nombre y apellidos para completar tu perfil",
                        "timestamp": timezone.now(),
                    }
                )

            return alerts

        except Exception as e:
            logger.exception(f"Error obteniendo alertas del usuario: {e}")
            return []

    @staticmethod
    def _get_error_dashboard():
        """
        Dashboard de error por defecto
        """
        return {
            "user_info": {},
            "stats": {},
            "mini_cards": [],
            "recent_activities": [],
            "alerts": [],
            "charts_data": {"basic_stats": True},
        }


class FinancialDashboardService:
    """
    Servicio para dashboard financiero con indicadores principales, filtros y gráficos
    """

    @staticmethod
    def get_financial_summary(user, year=None, month=None, account_id=None):
        """
        Obtiene resumen financiero con totales, filtros opcionales y movimientos recientes

        Args:
            user: Usuario autenticado
            year: Año a filtrar (opcional)
            month: Mes a filtrar (opcional, requiere year)
            account_id: ID de cuenta a filtrar (opcional)

        Returns:
            Dict con resumen financiero completo
        """

        from django.db.models import Q

        from accounts.models import Account
        from transactions.models import Transaction
        from utils.currency_converter import FxService

        try:
            # Obtener moneda base del usuario
            base_currency = FxService.get_base_currency(user)

            # Construir filtros
            filters = Q(user=user)

            # Filtro por fecha
            if year and month:
                filters &= Q(date__year=year, date__month=month)
            elif year:
                filters &= Q(date__year=year)

            # Filtro por cuenta
            if account_id:
                try:
                    account = Account.objects.get(id=account_id, user=user)
                    filters &= Q(origin_account=account)
                except Account.DoesNotExist:
                    return {
                        "error": f"Cuenta con ID {account_id} no encontrada",
                        "has_data": False,
                    }

            # Obtener transacciones filtradas
            transactions = Transaction.objects.filter(filters)

            # Verificar si hay datos
            has_data = transactions.exists()
            accounts = Account.objects.filter(user=user).count()

            if not has_data:
                return FinancialDashboardService._get_empty_state(
                    user, base_currency, has_accounts=accounts > 0
                )

            # Calcular totales por tipo de transacción
            totals = FinancialDashboardService._calculate_totals(transactions, base_currency, user)

            # Obtener movimientos recientes (últimos 5)
            recent_transactions = FinancialDashboardService._get_recent_transactions(
                user, account_id, limit=5
            )

            # Obtener facturas próximas a vencer (últimas 5)
            upcoming_bills = FinancialDashboardService._get_upcoming_bills(user, limit=5)

            # Datos para gráficos
            expense_distribution = FinancialDashboardService._get_expense_distribution(
                transactions, base_currency, user
            )

            daily_flow = FinancialDashboardService._get_daily_income_expense(
                transactions, base_currency, user, year, month
            )

            # Construir respuesta
            return {
                "has_data": True,
                "summary": {
                    "total_income": totals["income"],
                    "total_expenses": totals["expenses"],
                    "total_savings": totals["savings"],
                    "total_iva": totals["iva"],
                    "total_gmf": totals["gmf"],
                    "net_balance": totals["income"] - totals["expenses"],
                    "currency": base_currency,
                },
                "filters": {
                    "year": year,
                    "month": month,
                    "account_id": account_id,
                    "period_label": FinancialDashboardService._get_period_label(year, month),
                },
                "recent_transactions": recent_transactions,
                "upcoming_bills": upcoming_bills,
                "charts": {
                    "expense_distribution": expense_distribution,
                    "daily_flow": daily_flow,
                },
                "accounts_info": {
                    "total_accounts": accounts,
                    "has_accounts": accounts > 0,
                },
            }

        except Exception as e:
            logger.exception(f"Error obteniendo resumen financiero: {e}")
            return {
                "error": f"Error al obtener resumen financiero: {e!s}",
                "has_data": False,
            }

    @staticmethod
    def _calculate_totals(transactions, base_currency, user):
        """
        Calcula totales de ingresos, gastos, ahorros, IVA y GMF en moneda base
        """
        from utils.currency_converter import FxService

        totals = {
            "income": 0.0,
            "expenses": 0.0,
            "savings": 0.0,
            "iva": 0.0,
            "gmf": 0.0,
        }

        # Procesar transacciones por tipo y convertir a moneda base
        for tx in transactions:
            tx_currency = tx.transaction_currency or tx.origin_account.currency
            tx_date = tx.date

            # Convertir total_amount a moneda base
            converted_amount, _, _ = FxService.convert_to_base(
                tx.total_amount, tx_currency, base_currency, tx_date
            )

            # Sumar según tipo
            if tx.type == 1:  # Income
                totals["income"] += float(converted_amount)
            elif tx.type == 2:  # Expense
                totals["expenses"] += float(converted_amount)
            elif tx.type == 4:  # Saving
                totals["savings"] += float(converted_amount)

            # Sumar IVA (taxed_amount)
            if tx.taxed_amount:
                converted_tax, _, _ = FxService.convert_to_base(
                    tx.taxed_amount, tx_currency, base_currency, tx_date
                )
                totals["iva"] += float(converted_tax)

            # Sumar GMF (gmf_amount)
            if tx.gmf_amount:
                converted_gmf, _, _ = FxService.convert_to_base(
                    tx.gmf_amount, tx_currency, base_currency, tx_date
                )
                totals["gmf"] += float(converted_gmf)

        return totals

    @staticmethod
    def _get_recent_transactions(user, account_id=None, limit=5):
        """
        Obtiene los movimientos más recientes del usuario
        """
        from django.db.models import Q

        from transactions.models import Transaction

        filters = Q(user=user)
        if account_id:
            filters &= Q(origin_account_id=account_id)

        transactions = (
            Transaction.objects.filter(filters)
            .select_related("origin_account", "category", "destination_account")
            .order_by("-date", "-created_at")[:limit]
        )

        recent = []
        for tx in transactions:
            recent.append(
                {
                    "id": tx.id,
                    "type": tx.get_type_display(),
                    "type_code": tx.type,
                    "date": tx.date.isoformat(),
                    "description": tx.description or "Sin descripción",
                    "amount": tx.total_amount,
                    "amount_formatted": f"${tx.total_amount / 100:,.0f}",
                    "currency": tx.transaction_currency or tx.origin_account.currency,
                    "account": tx.origin_account.name,
                    "category": tx.category.name if tx.category else None,
                    "category_color": tx.category.color if tx.category else None,
                    "category_icon": tx.category.icon if tx.category else None,
                }
            )

        return recent

    @staticmethod
    def _get_expense_distribution(transactions, base_currency, user):
        """
        Calcula distribución de gastos por categoría (para gráfico de dona)
        """
        from utils.currency_converter import FxService

        # Filtrar solo gastos con categoría
        expenses = transactions.filter(type=2, category__isnull=False)

        if not expenses.exists():
            return {"categories": [], "total": 0, "has_data": False}

        # Agrupar por categoría
        category_totals = {}

        for tx in expenses:
            tx_currency = tx.transaction_currency or tx.origin_account.currency
            converted, _, _ = FxService.convert_to_base(
                tx.total_amount, tx_currency, base_currency, tx.date
            )

            cat_id = tx.category.id
            if cat_id not in category_totals:
                category_totals[cat_id] = {
                    "id": cat_id,
                    "name": tx.category.name,
                    "color": tx.category.color,
                    "icon": tx.category.icon,
                    "amount": 0.0,
                    "count": 0,
                }

            category_totals[cat_id]["amount"] += float(converted)
            category_totals[cat_id]["count"] += 1

        # Calcular total y porcentajes
        total_expenses = sum(cat["amount"] for cat in category_totals.values())

        categories = []
        for cat in category_totals.values():
            percentage = (cat["amount"] / total_expenses * 100) if total_expenses > 0 else 0
            categories.append(
                {
                    "id": cat["id"],
                    "name": cat["name"],
                    "amount": cat["amount"],
                    "count": cat["count"],
                    "percentage": round(percentage, 2),
                    "color": cat["color"],
                    "icon": cat["icon"],
                    "formatted": f"${cat['amount'] / 100:,.0f}",
                }
            )

        # Ordenar por monto descendente
        categories.sort(key=lambda x: x["amount"], reverse=True)

        return {
            "categories": categories,
            "total": total_expenses,
            "total_formatted": f"${total_expenses / 100:,.0f}",
            "has_data": True,
        }

    @staticmethod
    def _get_daily_income_expense(transactions, base_currency, user, year=None, month=None):
        """
        Calcula ingresos y gastos diarios (para gráfico de líneas)
        """
        from collections import defaultdict
        from datetime import date, timedelta

        from utils.currency_converter import FxService

        if not year or not month:
            # Usar mes actual si no se especifica
            today = date.today()
            year = today.year
            month = today.month

        # Filtrar transacciones del mes especificado
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

        month_transactions = transactions.filter(date__gte=start_date, date__lte=end_date)

        # Agrupar por fecha
        daily_data = defaultdict(lambda: {"income": 0.0, "expenses": 0.0})

        for tx in month_transactions:
            tx_currency = tx.transaction_currency or tx.origin_account.currency
            converted, _, _ = FxService.convert_to_base(
                tx.total_amount, tx_currency, base_currency, tx.date
            )

            date_key = tx.date.isoformat()

            if tx.type == 1:  # Income
                daily_data[date_key]["income"] += float(converted)
            elif tx.type == 2:  # Expense
                daily_data[date_key]["expenses"] += float(converted)

        # Generar series para todos los días del mes
        dates = []
        income_series = []
        expense_series = []

        current = start_date
        while current <= end_date:
            date_key = current.isoformat()
            dates.append(date_key)
            income_series.append(daily_data[date_key]["income"])
            expense_series.append(daily_data[date_key]["expenses"])
            current += timedelta(days=1)

        return {
            "dates": dates,
            "income": income_series,
            "expenses": expense_series,
            "total_income": sum(income_series),
            "total_expenses": sum(expense_series),
            "has_data": len(month_transactions) > 0,
        }

    @staticmethod
    def _get_empty_state(user, base_currency, has_accounts=False):
        """
        Retorna estado vacío cuando no hay transacciones
        """
        return {
            "has_data": False,
            "summary": {
                "total_income": 0.0,
                "total_expenses": 0.0,
                "total_savings": 0.0,
                "total_iva": 0.0,
                "total_gmf": 0.0,
                "net_balance": 0.0,
                "currency": base_currency,
            },
            "filters": {"year": None, "month": None, "account_id": None, "period_label": "Todos"},
            "recent_transactions": [],
            "upcoming_bills": [],
            "charts": {
                "expense_distribution": {"categories": [], "total": 0, "has_data": False},
                "daily_flow": {
                    "dates": [],
                    "income": [],
                    "expenses": [],
                    "total_income": 0,
                    "total_expenses": 0,
                    "has_data": False,
                },
            },
            "accounts_info": {"total_accounts": 0, "has_accounts": has_accounts},
            "empty_state": {
                "message": (
                    "No tienes movimientos registrados"
                    if has_accounts
                    else "No tienes cuentas creadas"
                ),
                "suggestion": (
                    "Registra tu primer movimiento"
                    if has_accounts
                    else "Crea una cuenta para empezar"
                ),
                "action": "create_transaction" if has_accounts else "create_account",
            },
        }

    @staticmethod
    def _get_period_label(year, month):
        """
        Genera etiqueta legible del período
        """
        if not year and not month:
            return "Todos los períodos"

        months_es = [
            "",
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre",
        ]

        if year and month:
            return f"{months_es[month]} {year}"
        if year:
            return f"Año {year}"

        return "Período personalizado"

    @staticmethod
    def _get_upcoming_bills(user, limit=5):
        """
        Obtiene las facturas próximas a vencer ordenadas por proximidad

        Args:
            user: Usuario propietario de las facturas
            limit: Número máximo de facturas a retornar (default: 5)

        Returns:
            list: Lista de diccionarios con información de facturas próximas a vencer
        """

        from bills.models import Bill

        # Obtener timezone del usuario
        try:
            user_tz = user.notification_preferences.timezone_object
        except Exception:
            import pytz

            user_tz = pytz.timezone("America/Bogota")

        # Filtrar facturas pendientes o atrasadas (no pagadas)
        bills = (
            Bill.objects.filter(user=user, status__in=[Bill.PENDING, Bill.OVERDUE])
            .select_related("suggested_account", "category")
            .order_by("due_date")[:limit]
        )

        upcoming = []
        for bill in bills:
            days_until = bill.days_until_due(user_tz=user_tz)

            # Determinar urgencia
            if days_until < 0:
                urgency = "overdue"
                urgency_label = "Vencida"
                urgency_color = "#EF4444"  # Rojo
            elif days_until == 0:
                urgency = "today"
                urgency_label = "Hoy"
                urgency_color = "#F59E0B"  # Naranja
            elif days_until <= 3:
                urgency = "urgent"
                urgency_label = "Urgente"
                urgency_color = "#F59E0B"  # Naranja
            elif days_until <= 7:
                urgency = "soon"
                urgency_label = "Próxima"
                urgency_color = "#3B82F6"  # Azul
            else:
                urgency = "normal"
                urgency_label = "Pendiente"
                urgency_color = "#6B7280"  # Gris

            # Formatear monto en centavos
            amount_cents = int(float(bill.amount) * 100)

            upcoming.append(
                {
                    "id": bill.id,
                    "provider": bill.provider,
                    "amount": amount_cents,  # Centavos
                    "amount_formatted": f"${bill.amount:,.0f}",
                    "due_date": bill.due_date.isoformat(),
                    "days_until_due": days_until,
                    "status": bill.status,
                    "urgency": urgency,
                    "urgency_label": urgency_label,
                    "urgency_color": urgency_color,
                    "suggested_account": (
                        bill.suggested_account.name if bill.suggested_account else None
                    ),
                    "suggested_account_id": (
                        bill.suggested_account.id if bill.suggested_account else None
                    ),
                    "category": bill.category.name if bill.category else None,
                    "category_color": bill.category.color if bill.category else None,
                    "category_icon": bill.category.icon if bill.category else None,
                    "description": bill.description or "",
                    "is_recurring": bill.is_recurring,
                }
            )

        return upcoming
