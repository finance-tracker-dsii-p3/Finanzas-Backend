from django.db.models.signals import post_save
from django.dispatch import receiver
from alerts.models import Alert
from budgets.models import Budget
from transactions.models import Transaction


@receiver(post_save, sender=Transaction)
def check_budget_after_transaction(sender, instance, **kwargs):
    """Crea una alerta si una transacción hace que se alcance o exceda un presupuesto."""
    if instance.type != "Expense":
        return

    category = instance.category
    user = instance.user

    budgets = Budget.objects.filter(category=category, user=user, is_active=True)

    for budget in budgets:
        percentage = budget.get_spent_percentage()

        # Already exceeded
        if percentage > 100:
            Alert.objects.get_or_create(
                user=user,
                budget=budget,
                alert_type=Alert.EXCEEDED,
                message=f"Has excedido el presupuesto de {category.name}.",
            )
            continue

        # Passed the alert threshold (e.g., 80%)
        if percentage >= budget.alert_threshold:
            Alert.objects.get_or_create(
                user=user,
                budget=budget,
                alert_type=Alert.WARNING,
                message=(
                    f"Has alcanzado el {percentage}% del presupuesto en "
                    f"{category.name}."
                ),
            )
