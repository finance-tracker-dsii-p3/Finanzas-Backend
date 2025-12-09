"""
Views para la gestión de cuentas financieras
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from decimal import Decimal
import logging

from .models import Account, AccountOption, AccountOptionType
from .serializers import (
    AccountListSerializer,
    AccountDetailSerializer,
    AccountCreateSerializer,
    AccountUpdateSerializer,
    AccountBalanceUpdateSerializer,
    AccountSummarySerializer,
)
from .services import AccountService

logger = logging.getLogger(__name__)


class AccountViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para gestión de cuentas financieras

    Proporciona operaciones CRUD completas más acciones adicionales
    para resúmenes, balances y estadísticas.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filtrar cuentas por usuario autenticado"""
        return Account.objects.filter(user=self.request.user).order_by("name")

    def get_serializer_class(self):
        """Seleccionar serializer según la acción"""
        if self.action == "list":
            return AccountListSerializer
        elif self.action == "retrieve":
            return AccountDetailSerializer
        elif self.action == "create":
            return AccountCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return AccountUpdateSerializer
        elif self.action == "update_balance":
            return AccountBalanceUpdateSerializer
        elif self.action == "summary":
            return AccountSummarySerializer
        else:
            return AccountDetailSerializer

    def perform_create(self, serializer):
        """Crear cuenta asignando el usuario autenticado"""
        try:
            # El serializer ya maneja la creación con el usuario
            account = serializer.save()

            logger.info(
                f"Usuario {self.request.user.id} creó cuenta: {account.name} "
                f"({account.get_category_display()})"
            )

        except Exception as e:
            logger.warning(f"Error al crear cuenta para usuario {self.request.user.id}: {str(e)}")
            raise e

    def perform_update(self, serializer):
        """Actualizar cuenta"""
        try:
            # El serializer ya maneja la actualización
            account = serializer.save()

            logger.info(f"Usuario {self.request.user.id} actualizó cuenta: {account.name}")

        except Exception as e:
            logger.warning(f"Error al actualizar cuenta {self.get_object().id}: {str(e)}")
            raise e

    def perform_destroy(self, instance):
        """Eliminar cuenta con validaciones"""
        try:
            # Validar eliminación
            validation = AccountService.validate_account_deletion_with_confirmation(
                account=instance, force=self.request.data.get("force", False)
            )

            if not validation["can_delete"]:
                raise ValueError("; ".join(validation["errors"]))

            # Eliminar usando service
            AccountService.delete_account(instance)

            logger.info(f"Usuario {self.request.user.id} eliminó cuenta: {instance.name}")

        except ValueError as e:
            logger.warning(f"Error al eliminar cuenta {instance.id}: {str(e)}")
            raise e

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """
        Obtener resumen financiero del usuario

        Returns:
            Response: Resumen con totales, patrimonio neto, estadísticas
        """
        try:
            summary_data = AccountService.get_accounts_summary(request.user)

            logger.info(f"Generado resumen financiero para usuario {request.user.id}")

            return Response(summary_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error al generar resumen para usuario {request.user.id}: {str(e)}")
            return Response(
                {"error": "Error interno al generar resumen"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def by_currency(self, request):
        """
        Obtener cuentas filtradas por moneda

        Query params:
            currency (str): Código de moneda (COP, USD, EUR)

        Returns:
            Response: Lista de cuentas en la moneda especificada
        """
        currency = request.query_params.get("currency")

        if not currency:
            return Response(
                {"error": "Parámetro currency es requerido"}, status=status.HTTP_400_BAD_REQUEST
            )

        if currency not in dict(Account.CURRENCY_CHOICES):
            return Response(
                {"error": f"Moneda {currency} no válida"}, status=status.HTTP_400_BAD_REQUEST
            )

        accounts = AccountService.get_accounts_by_currency(request.user, currency)
        serializer = AccountListSerializer(accounts, many=True)

        logger.info(
            f"Usuario {request.user.id} consultó cuentas en {currency}: "
            f"{accounts.count()} encontradas"
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def credit_cards_summary(self, request):
        """
        Obtener resumen específico de tarjetas de crédito

        Returns:
            Response: Estadísticas de tarjetas de crédito
        """
        try:
            summary = AccountService.get_credit_cards_summary(request.user)

            logger.info(f"Generado resumen de tarjetas para usuario {request.user.id}")

            return Response(summary, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(
                f"Error al generar resumen de tarjetas para usuario {request.user.id}: {str(e)}"
            )
            return Response(
                {"error": "Error interno al generar resumen de tarjetas"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def update_balance(self, request, pk=None):
        """
        Actualizar saldo manualmente (ajuste de balance)

        Body:
            new_balance (decimal): Nuevo saldo
            reason (str, optional): Razón del ajuste

        Returns:
            Response: Cuenta actualizada
        """
        account = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            try:
                new_balance = serializer.validated_data["new_balance"]
                reason = serializer.validated_data.get("reason")

                updated_account = AccountService.update_account_balance(
                    account=account, new_balance=new_balance, reason=reason
                )

                response_serializer = AccountDetailSerializer(updated_account)

                logger.info(
                    f"Usuario {request.user.id} actualizó saldo de cuenta {account.name}: "
                    f"{account.current_balance} -> {new_balance} ({reason or 'Sin razón'})"
                )

                return Response(response_serializer.data, status=status.HTTP_200_OK)

            except ValueError as e:
                logger.warning(f"Error al actualizar saldo de cuenta {account.id}: {str(e)}")
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def validate_deletion(self, request, pk=None):
        """
        Validar si una cuenta puede ser eliminada

        Body:
            force (bool, optional): Si forzar validación

        Returns:
            Response: Resultado de validación con advertencias/errores
        """
        account = self.get_object()
        force = request.data.get("force", False)

        try:
            validation_result = AccountService.validate_account_deletion_with_confirmation(
                account=account, force=force
            )

            logger.info(
                f"Usuario {request.user.id} validó eliminación de cuenta {account.name}: "
                f"can_delete={validation_result['can_delete']}"
            )

            return Response(validation_result, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error al validar eliminación de cuenta {account.id}: {str(e)}")
            return Response(
                {"error": "Error interno en validación"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"])
    def categories_stats(self, request):
        """
        Obtener estadísticas por categorías de cuentas

        Returns:
            Response: Estadísticas agrupadas por categoría
        """
        try:
            accounts = self.get_queryset().filter(is_active=True)

            stats = {}
            for account in accounts:
                category = account.get_category_display()

                if category not in stats:
                    stats[category] = {"count": 0, "total_balance": Decimal("0.00"), "accounts": []}

                stats[category]["count"] += 1
                stats[category]["total_balance"] += account.balance_for_totals
                stats[category]["accounts"].append(
                    {
                        "id": account.id,
                        "name": account.name,
                        "balance": account.current_balance,
                        "currency": account.currency,
                    }
                )

            logger.info(
                f"Generadas estadísticas por categoría para usuario {request.user.id}: "
                f"{len(stats)} categorías"
            )

            return Response(stats, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(
                f"Error al generar estadísticas por categoría para usuario {request.user.id}: {str(e)}"
            )
            return Response(
                {"error": "Error interno al generar estadísticas"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        """
        Activar/desactivar cuenta

        Returns:
            Response: Cuenta actualizada
        """
        account = self.get_object()

        try:
            # Permitir desactivar cuenta con saldo (solo advertencia, no bloqueo)

            account.is_active = not account.is_active
            account.save(update_fields=["is_active", "updated_at"])

            action_text = "activó" if account.is_active else "desactivó"
            logger.info(f"Usuario {request.user.id} {action_text} cuenta: {account.name}")

            serializer = AccountDetailSerializer(account)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error al cambiar estado de cuenta {account.id}: {str(e)}")
            return Response(
                {"error": "Error interno al cambiar estado"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def list(self, request, *args, **kwargs):
        """
        Listar cuentas del usuario con filtros opcionales

        Query params:
            active_only (bool): Solo cuentas activas (default: false - devuelve todas)
            category (str): Filtrar por categoría
            account_type (str): Filtrar por tipo (asset/liability)

        Returns:
            Response: Lista de cuentas
        """
        queryset = self.get_queryset()

        # Filtro por cuentas activas (solo si se solicita explícitamente)
        active_only = request.query_params.get("active_only", "false").lower() == "true"
        if active_only:
            queryset = queryset.filter(is_active=True)

        # Filtro por categoría
        category = request.query_params.get("category")
        if category:
            queryset = queryset.filter(category=category)

        # Filtro por tipo
        account_type = request.query_params.get("account_type")
        if account_type:
            queryset = queryset.filter(account_type=account_type)

        serializer = self.get_serializer(queryset, many=True)

        logger.info(f"Usuario {request.user.id} listó cuentas: {queryset.count()} encontradas")

        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_account_options(request):
    """
    Retorna los listados de opciones para crear cuentas.
    Incluye bancos, billeteras y bancos para tarjetas de crédito.

    Returns:
        Response: Diccionario con los listados de opciones
    """
    try:
        # Obtener bancos activos ordenados
        banks = (
            AccountOption.objects.filter(option_type=AccountOptionType.BANK, is_active=True)
            .order_by("order", "name")
            .values_list("name", flat=True)
        )

        # Obtener billeteras activas ordenadas
        wallets = (
            AccountOption.objects.filter(option_type=AccountOptionType.WALLET, is_active=True)
            .order_by("order", "name")
            .values_list("name", flat=True)
        )

        # Obtener bancos para tarjetas de crédito activos ordenados
        credit_card_banks = (
            AccountOption.objects.filter(
                option_type=AccountOptionType.CREDIT_CARD_BANK, is_active=True
            )
            .order_by("order", "name")
            .values_list("name", flat=True)
        )

        logger.info(
            f"Usuario {request.user.id} consultó opciones de cuentas: "
            f"{banks.count()} bancos, {wallets.count()} billeteras, "
            f"{credit_card_banks.count()} bancos para tarjetas"
        )

        return Response(
            {
                "banks": list(banks),
                "wallets": list(wallets),
                "credit_card_banks": list(credit_card_banks),
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"Error al obtener opciones de cuentas: {str(e)}")
        return Response(
            {"error": "Error al obtener opciones de cuentas"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
