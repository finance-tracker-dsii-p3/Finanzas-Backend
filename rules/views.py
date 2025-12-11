"""
Vistas para reglas automáticas (HU-12)
"""

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import AutomaticRule
from .serializers import (
    AutomaticRuleCreateSerializer,
    AutomaticRuleDetailSerializer,
    AutomaticRuleListSerializer,
    AutomaticRuleStatsSerializer,
    AutomaticRuleUpdateSerializer,
)
from .services import AutomaticRuleService, RuleEngineService


class AutomaticRuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión completa de reglas automáticas
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_active", "criteria_type", "action_type"]

    def get_queryset(self):
        """Filtrar reglas por usuario autenticado"""
        return AutomaticRule.objects.filter(user=self.request.user).order_by("order", "created_at")

    def get_serializer_class(self):
        """Seleccionar serializer según la acción"""
        if self.action == "list":
            return AutomaticRuleListSerializer
        if self.action == "retrieve":
            return AutomaticRuleDetailSerializer
        if self.action == "create":
            return AutomaticRuleCreateSerializer
        if self.action in ["update", "partial_update"]:
            return AutomaticRuleUpdateSerializer
        return AutomaticRuleListSerializer

    def get_serializer_context(self):
        """Agregar request al contexto del serializer"""
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def list(self, request, *args, **kwargs):
        """
        Listar reglas automáticas del usuario

        Query parameters:
        - active_only: true/false - Solo reglas activas
        - criteria_type: description_contains/transaction_type - Filtrar por tipo de criterio
        - action_type: assign_category/assign_tag - Filtrar por tipo de acción
        - search: texto - Buscar en nombre de regla y palabra clave
        """
        queryset = self.get_queryset()

        # Filtro adicional por activo
        active_only = request.query_params.get("active_only", "false").lower()
        if active_only == "true":
            queryset = queryset.filter(is_active=True)

        # Búsqueda por texto
        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(keyword__icontains=search))

        # Aplicar filtros del DjangoFilterBackend
        queryset = self.filter_queryset(queryset)

        # Paginación
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        # Mensaje personalizado si no hay reglas
        if not serializer.data:
            return Response(
                {
                    "count": 0,
                    "results": [],
                    "message": "Aún no tienes reglas automáticas configuradas. ¡Crea una para automatizar la categorización de tus movimientos!",
                }
            )

        return Response({"count": len(serializer.data), "results": serializer.data})

    def create(self, request, *args, **kwargs):
        """Crear nueva regla automática"""
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                # Formatear errores de validación de manera más clara
                errors = {}
                for field, field_errors in serializer.errors.items():
                    if isinstance(field_errors, list):
                        errors[field] = field_errors[0] if field_errors else "Error de validación"
                    else:
                        errors[field] = str(field_errors)

                return Response(
                    {
                        "error": "Datos de entrada inválidos",
                        "details": errors,
                        "message": "Por favor corrige los siguientes errores:",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            rule = AutomaticRuleService.create_rule(
                user=request.user, validated_data=serializer.validated_data
            )

            response_serializer = AutomaticRuleDetailSerializer(rule)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Capturar cualquier error no previsto
            return Response(
                {
                    "error": "Error interno al crear la regla",
                    "message": str(e),
                    "details": {
                        "type": type(e).__name__,
                        "suggestion": "Verifica que todos los campos requeridos estén presentes y sean válidos",
                    },
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, *args, **kwargs):
        """Actualizar regla automática completa"""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        updated_rule = AutomaticRuleService.update_rule(
            rule=instance, validated_data=serializer.validated_data
        )

        response_serializer = AutomaticRuleDetailSerializer(updated_rule)
        return Response(response_serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Eliminar regla automática"""
        instance = self.get_object()

        result = AutomaticRuleService.delete_rule(instance)

        return Response(
            {
                "message": result["message"],
                "deleted_rule": result["deleted_rule"],
                "affected_transactions": result["affected_transactions"],
            }
        )

    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        """
        Activar o desactivar una regla automática
        """
        rule = self.get_object()

        updated_rule = AutomaticRuleService.toggle_rule_active(rule)

        serializer = AutomaticRuleDetailSerializer(updated_rule)

        status_text = "activada" if updated_rule.is_active else "desactivada"

        return Response(
            {
                "message": f'Regla "{updated_rule.name}" {status_text} exitosamente.',
                "rule": serializer.data,
            }
        )

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """
        Obtener estadísticas de reglas automáticas del usuario
        """
        stats = AutomaticRuleService.get_rule_statistics(request.user)

        serializer = AutomaticRuleStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def reorder(self, request):
        """
        Reordenar reglas automáticas

        Body esperado:
        {
            "rule_orders": [
                {"id": 1, "order": 1},
                {"id": 2, "order": 2},
                ...
            ]
        }
        """
        rule_orders = request.data.get("rule_orders", [])

        if not rule_orders:
            return Response(
                {"error": "Se requiere el campo rule_orders con lista de IDs y órdenes"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            updated_rules = AutomaticRuleService.reorder_rules(
                user=request.user, rule_orders=rule_orders
            )

            serializer = AutomaticRuleListSerializer(updated_rules, many=True)

            return Response(
                {
                    "message": f"{len(updated_rules)} reglas reordenadas exitosamente.",
                    "rules": serializer.data,
                }
            )

        except Exception as e:
            return Response(
                {"error": f"Error reordenando reglas: {e!s}"}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["post"])
    def preview(self, request):
        """
        Previsualizar qué regla se aplicaría a una transacción

        Body esperado:
        {
            "description": "Pago Uber",
            "transaction_type": 2  // Opcional
        }
        """
        description = request.data.get("description")
        transaction_type = request.data.get("transaction_type")

        if not description and transaction_type is None:
            return Response(
                {"error": "Se requiere al menos description o transaction_type"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        preview = RuleEngineService.preview_rule_application(
            user=request.user, description=description, transaction_type=transaction_type
        )

        return Response(preview)

    @action(detail=False, methods=["get"])
    def active(self, request):
        """
        Obtener solo las reglas activas ordenadas por prioridad
        """
        active_rules = AutomaticRuleService.get_user_rules(user=request.user, active_only=True)

        serializer = AutomaticRuleListSerializer(active_rules, many=True)

        return Response(
            {
                "count": len(serializer.data),
                "results": serializer.data,
                "message": "Reglas activas ordenadas por prioridad",
            }
        )

    @action(detail=True, methods=["get"])
    def applied_transactions(self, request, pk=None):
        """
        Obtener transacciones a las que se ha aplicado esta regla
        """
        rule = self.get_object()

        # Importar aquí para evitar dependencias circulares
        from transactions.models import Transaction

        transactions = Transaction.objects.filter(applied_rule=rule).order_by("-created_at")[
            :20
        ]  # Últimas 20

        # Serializer simple para evitar dependencias circulares
        transactions_data = []
        for t in transactions:
            transactions_data.append(
                {
                    "id": t.id,
                    "total_amount": t.total_amount,
                    "date": t.date,
                    "description": t.description,
                    "type": t.get_type_display(),
                    "created_at": t.created_at,
                }
            )

        return Response(
            {
                "rule_name": rule.name,
                "total_applied": rule.applied_transactions.count(),
                "recent_transactions": transactions_data,
            }
        )
