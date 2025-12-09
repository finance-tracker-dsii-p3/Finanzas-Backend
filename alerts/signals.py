from django.db.models.signals import post_save
from django.dispatch import receiver
from alerts.models import Alert
from budgets.models import Budget
from transactions.models import Transaction
from notifications.engine import NotificationEngine


@receiver(post_save, sender=Transaction)
def check_budget_after_transaction(sender, instance, **kwargs):
    """
    Crea una alerta de presupuesto cuando una transacción de gasto hace que se
    alcance el 80 % (o el umbral configurado) o se exceda el 100 % del límite.

    Reglas importantes (HU-08):
    - Solo se consideran transacciones de gasto (type = 2).
    - Una alerta por presupuesto / nivel (warning o exceeded) y por mes.
    - Se apoya en created_at para identificar el mes de la alerta.
    
    Además genera notificaciones respetando preferencias del usuario (HU-18).
    """
    # Solo procesar en creación (no en actualización)
    if kwargs.get("created", False) is False:
        return

    # Solo gastos
    if instance.type != 2:
        return

    # Debe tener categoría para poder asociarla a un presupuesto
    if not instance.category:
        return

    category = instance.category
    user = instance.user

    # Obtener la moneda de la cuenta de origen de la transacción
    transaction_currency = instance.origin_account.currency if instance.origin_account else None

    if not transaction_currency:
        return

    # Presupuestos activos del usuario para esa categoría y moneda
    budgets = Budget.objects.filter(
        category=category,
        user=user,
        is_active=True,
        currency=transaction_currency,  # Solo presupuestos con la misma moneda
    )

    for budget in budgets:
        # Usar la fecha de la transacción como referencia del período
        percentage = budget.get_spent_percentage(reference_date=instance.date)
        spent = budget.get_spent_amount(reference_date=instance.date)
        limit = budget.amount

        # Determinar tipo de alerta a generar, si aplica
        alert_type = None
        if percentage >= 100:
            alert_type = "exceeded"
        elif percentage >= budget.alert_threshold:
            alert_type = "warning"

        if not alert_type:
            continue

        # Evitar repetir alertas para el mismo presupuesto / tipo / mes
        # Usamos la fecha de la transacción para determinar el mes de la alerta
        transaction_year = instance.date.year
        transaction_month = instance.date.month

        # Buscar si ya existe una alerta para este presupuesto/tipo/mes
        # usando los campos transaction_year y transaction_month
        existing = Alert.objects.filter(
            user=user,
            budget=budget,
            alert_type=alert_type,
            transaction_year=transaction_year,
            transaction_month=transaction_month,
        ).exists()

        if existing:
            # Ya existe una alerta para este mes, no crear otra
            continue

        # Crear nueva alerta para este mes
        Alert.objects.create(
            user=user,
            budget=budget,
            alert_type=alert_type,
            transaction_year=transaction_year,
            transaction_month=transaction_month,
        )
        
        # Crear notificación respetando preferencias del usuario (HU-18)
        try:
            if alert_type == "exceeded":
                NotificationEngine.create_budget_exceeded(
                    user=user,
                    budget=budget,
                    spent=spent,
                    limit=limit
                )
            else:  # warning
                NotificationEngine.create_budget_warning(
                    user=user,
                    budget=budget,
                    percentage=percentage,
                    spent=spent,
                    limit=limit
                )
        except Exception:
            # No fallar la transacción si hay error en la notificación
            pass

