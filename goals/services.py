from django.db import transaction as db_transaction
from django.db.models import F
from .models import Goal
from notifications.services import NotificationService
from notifications.models import Notification
import logging

logger = logging.getLogger(__name__)


class GoalService:

    @staticmethod
    @db_transaction.atomic
    def assign_transaction_to_goal(transaction, goal):
        if transaction.type != 4:
            raise ValueError("Solo se pueden asignar transacciones tipo Saving a metas")
        
        if transaction.user != goal.user:
            raise ValueError("La transacción y la meta deben pertenecer al mismo usuario")
        
        account_currency = transaction.origin_account.currency
        if account_currency != goal.currency:
            raise ValueError(
                f"La moneda de la cuenta ({account_currency}) no coincide con la moneda de la meta ({goal.currency}). "
                f"Las transacciones deben estar en la misma moneda que la meta."
            )
        
        old_saved_amount = goal.saved_amount
        transaction_amount = transaction.total_amount
        
        Goal.objects.filter(pk=goal.pk).update(
            saved_amount=F('saved_amount') + transaction_amount
        )
        
        goal.refresh_from_db()
        
        logger.info(
            f"Transacción {transaction.id} asignada a meta {goal.id}. "
            f"Meta actualizada: ${old_saved_amount} -> ${goal.saved_amount}"
        )
        
        GoalService._check_goal_progress(goal, transaction_amount)
        
        return goal

    @staticmethod
    @db_transaction.atomic
    def remove_transaction_from_goal(transaction, goal):
        transaction_amount = transaction.total_amount
        
        Goal.objects.filter(pk=goal.pk).update(
            saved_amount=F('saved_amount') - transaction_amount
        )
        
        goal.refresh_from_db()
        
        logger.info(
            f"Transacción {transaction.id} removida de meta {goal.id}. "
            f"Meta actualizada: ${goal.saved_amount}"
        )

    @staticmethod
    def _check_goal_progress(goal, transaction_amount):
        remaining = goal.get_remaining_amount()
        
        if goal.is_completed():
            NotificationService.create_notification(
                user=goal.user,
                notification_type=Notification.SYSTEM_ALERT,
                title="¡Meta alcanzada! 🎉",
                message=f"Has alcanzado tu meta '{goal.name}'. ¡Felicidades!",
                related_object_id=goal.id
            )
            logger.info(f"Meta {goal.id} alcanzada - notificación enviada")
        
        elif remaining > 0 and remaining <= 300000:
            NotificationService.create_notification(
                user=goal.user,
                notification_type=Notification.SYSTEM_ALERT,
                title="¡Casi lo logras! 💪",
                message=f"Te faltan ${remaining:,} para alcanzar tu meta '{goal.name}'",
                related_object_id=goal.id
            )
            logger.info(f"Meta {goal.id} cerca de alcanzarse - notificación enviada")

