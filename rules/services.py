"""
Servicios para reglas automáticas (HU-12)
Motor de reglas que aplica automáticamente categorías y etiquetas
"""

import logging
from typing import List, Dict, Any
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import AutomaticRule

User = get_user_model()
logger = logging.getLogger(__name__)


class RuleEngineService:
    """
    Motor de reglas automáticas para transacciones
    """

    @staticmethod
    def apply_rules_to_transaction(transaction_obj) -> Dict[str, Any]:
        """
        Aplica reglas automáticas a una transacción.

        Args:
            transaction_obj: Instancia de Transaction

        Returns:
            Dict con información sobre la regla aplicada:
            {
                'rule_applied': bool,
                'rule_name': str | None,
                'action_type': str | None,
                'changes': dict,
                'message': str
            }
        """
        logger.info(f"Aplicando reglas a transacción ID {transaction_obj.id}")

        result = {
            "rule_applied": False,
            "rule_name": None,
            "action_type": None,
            "changes": {},
            "message": "No se aplicó ninguna regla",
        }

        try:
            # Obtener reglas activas del usuario, ordenadas por prioridad
            rules = AutomaticRule.objects.filter(
                user=transaction_obj.user, is_active=True
            ).order_by("order", "created_at")

            if not rules.exists():
                result["message"] = "No hay reglas activas configuradas"
                return result

            # Aplicar la primera regla que coincida
            for rule in rules:
                if rule.matches_transaction(transaction_obj):
                    rule_result = rule.apply_to_transaction(transaction_obj)

                    if rule_result["applied"]:
                        # Guardar la transacción con los cambios aplicados
                        transaction_obj.save()

                        result.update(
                            {
                                "rule_applied": True,
                                "rule_name": rule_result["rule_name"],
                                "action_type": rule_result["action_type"],
                                "changes": rule_result["changes"],
                                "message": f'Regla "{rule.name}" aplicada exitosamente',
                            }
                        )

                        logger.info(
                            f"Regla '{rule.name}' aplicada a transacción {transaction_obj.id}"
                        )
                        break

            if not result["rule_applied"]:
                result["message"] = "Ninguna regla coincide con esta transacción"

        except Exception as e:
            logger.error(f"Error aplicando reglas a transacción {transaction_obj.id}: {str(e)}")
            result["message"] = f"Error aplicando reglas: {str(e)}"

        return result

    @staticmethod
    def get_matching_rules(
        user, description: str = None, transaction_type: int = None
    ) -> List[AutomaticRule]:
        """
        Obtiene las reglas que coincidirían con los criterios dados.

        Args:
            user: Usuario propietario
            description: Descripción de la transacción
            transaction_type: Tipo de transacción

        Returns:
            Lista de reglas que coinciden
        """
        matching_rules = []

        rules = AutomaticRule.objects.filter(user=user, is_active=True).order_by(
            "order", "created_at"
        )

        for rule in rules:
            matches = False

            if rule.criteria_type == AutomaticRule.DESCRIPTION_CONTAINS:
                if description and rule.keyword:
                    matches = rule.keyword.lower() in description.lower()

            elif rule.criteria_type == AutomaticRule.TRANSACTION_TYPE:
                if transaction_type is not None:
                    matches = rule.target_transaction_type == transaction_type

            if matches:
                matching_rules.append(rule)

        return matching_rules

    @staticmethod
    def preview_rule_application(
        user, description: str = None, transaction_type: int = None
    ) -> Dict[str, Any]:
        """
        Previsualiza qué regla se aplicaría sin hacer cambios reales.

        Args:
            user: Usuario propietario
            description: Descripción de la transacción
            transaction_type: Tipo de transacción

        Returns:
            Dict con información de la regla que se aplicaría
        """
        matching_rules = RuleEngineService.get_matching_rules(user, description, transaction_type)

        if not matching_rules:
            return {
                "will_apply": False,
                "rule": None,
                "message": "No hay reglas que coincidan con estos criterios",
            }

        # La primera regla es la que se aplicaría (por orden de prioridad)
        first_rule = matching_rules[0]

        return {
            "will_apply": True,
            "rule": {
                "id": first_rule.id,
                "name": first_rule.name,
                "action_type": first_rule.action_type,
                "target_category": first_rule.target_category.name
                if first_rule.target_category
                else None,
                "target_tag": first_rule.target_tag,
            },
            "message": f'Se aplicará la regla "{first_rule.name}"',
        }


class AutomaticRuleService:
    """
    Servicios para gestión de reglas automáticas
    """

    @staticmethod
    def get_user_rules(user, active_only: bool = False) -> List[AutomaticRule]:
        """
        Obtiene las reglas de un usuario.

        Args:
            user: Usuario propietario
            active_only: Solo reglas activas

        Returns:
            QuerySet de reglas
        """
        queryset = AutomaticRule.objects.filter(user=user)

        if active_only:
            queryset = queryset.filter(is_active=True)

        return queryset.order_by("order", "created_at")

    @staticmethod
    def create_rule(user, validated_data: Dict[str, Any]) -> AutomaticRule:
        """
        Crea una nueva regla automática.

        Args:
            user: Usuario propietario
            validated_data: Datos validados de la regla

        Returns:
            Instancia de AutomaticRule creada
        """
        validated_data["user"] = user

        # Si no se especifica orden, usar el siguiente disponible
        if "order" not in validated_data or validated_data["order"] == 0:
            from django.db import models

            max_order = (
                AutomaticRule.objects.filter(user=user).aggregate(models.Max("order"))["order__max"]
                or 0
            )
            validated_data["order"] = max_order + 1

        return AutomaticRule.objects.create(**validated_data)

    @staticmethod
    def update_rule(rule: AutomaticRule, validated_data: Dict[str, Any]) -> AutomaticRule:
        """
        Actualiza una regla existente.

        Args:
            rule: Instancia de AutomaticRule
            validated_data: Datos validados para actualizar

        Returns:
            Instancia actualizada
        """
        for field, value in validated_data.items():
            setattr(rule, field, value)

        rule.save()
        return rule

    @staticmethod
    def delete_rule(rule: AutomaticRule) -> Dict[str, Any]:
        """
        Elimina una regla y actualiza las transacciones afectadas.

        Args:
            rule: Instancia de AutomaticRule a eliminar

        Returns:
            Dict con información sobre la eliminación
        """
        rule_name = rule.name
        affected_transactions = rule.applied_transactions.count()

        # Limpiar referencia en transacciones afectadas
        rule.applied_transactions.update(applied_rule=None)

        rule.delete()

        return {
            "deleted_rule": rule_name,
            "affected_transactions": affected_transactions,
            "message": f'Regla "{rule_name}" eliminada. Se limpiaron {affected_transactions} transacciones afectadas.',
        }

    @staticmethod
    def toggle_rule_active(rule: AutomaticRule) -> AutomaticRule:
        """
        Activa o desactiva una regla.

        Args:
            rule: Instancia de AutomaticRule

        Returns:
            Instancia actualizada
        """
        rule.is_active = not rule.is_active
        rule.save()
        return rule

    @staticmethod
    def reorder_rules(user, rule_orders: List[Dict[str, int]]) -> List[AutomaticRule]:
        """
        Reordena las reglas de un usuario.

        Args:
            user: Usuario propietario
            rule_orders: Lista de {'id': rule_id, 'order': new_order}

        Returns:
            Lista de reglas actualizadas
        """
        updated_rules = []

        with transaction.atomic():
            for item in rule_orders:
                try:
                    rule = AutomaticRule.objects.get(id=item["id"], user=user)
                    rule.order = item["order"]
                    rule.save()
                    updated_rules.append(rule)
                except AutomaticRule.DoesNotExist:
                    continue

        return updated_rules

    @staticmethod
    def get_rule_statistics(user) -> Dict[str, Any]:
        """
        Obtiene estadísticas de las reglas de un usuario.

        Args:
            user: Usuario propietario

        Returns:
            Dict con estadísticas
        """
        rules = AutomaticRule.objects.filter(user=user)

        total_rules = rules.count()
        active_rules = rules.filter(is_active=True).count()
        inactive_rules = total_rules - active_rules

        # Contar aplicaciones totales
        total_applications = 0
        most_used_rule = None
        max_applications = 0

        for rule in rules:
            applications = rule.applied_transactions.count()
            total_applications += applications

            if applications > max_applications:
                max_applications = applications
                most_used_rule = {"id": rule.id, "name": rule.name, "applications": applications}

        # Aplicaciones recientes (últimas 5)
        from transactions.models import Transaction

        recent_applications = (
            Transaction.objects.filter(user=user, applied_rule__isnull=False)
            .select_related("applied_rule")
            .order_by("-created_at")[:5]
        )

        recent_list = []
        for trans in recent_applications:
            recent_list.append(
                {
                    "transaction_id": trans.id,
                    "rule_name": trans.applied_rule.name,
                    "amount": trans.total_amount,
                    "date": trans.date,
                    "created_at": trans.created_at,
                }
            )

        return {
            "total_rules": total_rules,
            "active_rules": active_rules,
            "inactive_rules": inactive_rules,
            "total_applications": total_applications,
            "most_used_rule": most_used_rule or {},
            "recent_applications": recent_list,
        }
