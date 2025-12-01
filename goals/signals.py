from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from transactions.models import Transaction
from goals.services import GoalService
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Transaction)
def update_goal_on_saving_transaction(sender, instance, **kwargs):
    if kwargs.get("created", False) is False:
        return

    if instance.type != 4:
        return

    if not instance.goal:
        return

    try:
        GoalService.assign_transaction_to_goal(instance, instance.goal)
        logger.info(f"Meta {instance.goal.id} actualizada por transacción {instance.id}")
    except Exception as e:
        logger.error(
            f"Error actualizando meta {instance.goal.id} con transacción {instance.id}: {str(e)}"
        )


@receiver(pre_delete, sender=Transaction)
def remove_transaction_from_goal(sender, instance, **kwargs):
    if instance.type != 4:
        return

    if not instance.goal:
        return

    try:
        GoalService.remove_transaction_from_goal(instance, instance.goal)
        logger.info(f"Transacción {instance.id} removida de meta {instance.goal.id}")
    except Exception as e:
        logger.error(
            f"Error removiendo transacción {instance.id} de meta {instance.goal.id}: {str(e)}"
        )
