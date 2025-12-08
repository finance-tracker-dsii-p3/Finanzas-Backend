from rest_framework import serializers
from transactions.models import Transaction
from categories.models import Category
from accounts.models import Account
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class TransactionDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True, allow_null=True)
    category_color = serializers.CharField(source="category.color", read_only=True, allow_null=True)
    category_icon = serializers.CharField(source="category.icon", read_only=True, allow_null=True)
    origin_account_name = serializers.CharField(source="origin_account.name", read_only=True)
    origin_account_currency = serializers.CharField(
        source="origin_account.currency", read_only=True
    )
    destination_account_name = serializers.CharField(
        source="destination_account.name", read_only=True, allow_null=True
    )
    goal_name = serializers.CharField(source="goal.name", read_only=True, allow_null=True)
    applied_rule_name = serializers.CharField(
        source="applied_rule.name", read_only=True, allow_null=True
    )

    class Meta:
        model = Transaction
        fields = [
            "id",
            "user",
            "origin_account",
            "origin_account_name",
            "destination_account",
            "destination_account_name",
            "category",
            "category_name",
            "category_color",
            "category_icon",
            "type",
            "base_amount",
            "tax_percentage",
            "taxed_amount",
            "gmf_amount",
            "capital_amount",
            "interest_amount",
            "total_amount",
            "date",
            "tag",
            "note",
            "description",
            "applied_rule",
            "applied_rule_name",
            "goal",
            "goal_name",
            "transaction_currency",  # Moneda de la transacción
            "exchange_rate",  # Tasa de cambio
            "original_amount",  # Monto original
            "origin_account_currency",  # Moneda de la cuenta (para mostrar)
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
            "updated_at",
        ]


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "user",
            "origin_account",
            "destination_account",
            "category",
            "type",
            "base_amount",
            "tax_percentage",
            "taxed_amount",
            "gmf_amount",
            "capital_amount",
            "interest_amount",
            "total_amount",
            "date",
            "tag",
            "note",
            "description",
            "applied_rule",
            "goal",  # HU-11: Meta de ahorro
            "transaction_currency",  # Moneda de la transacción
            "exchange_rate",  # Tasa de cambio
            "original_amount",  # Monto original antes de conversión
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "gmf_amount", "applied_rule", "created_at", "updated_at"]
        extra_kwargs = {
            "tag": {"required": False},
            "note": {"required": False},
            "description": {"required": False},
            "category": {"required": False},
            "capital_amount": {"required": False},
            "interest_amount": {"required": False},
            "base_amount": {"required": False},  # Opcional si viene total_amount + tax_percentage
            "tax_percentage": {"required": False},
            "total_amount": {"required": False},  # Opcional si viene base_amount
            "taxed_amount": {"read_only": True},
            "goal": {"required": False},
            "transaction_currency": {"required": False},
            "exchange_rate": {"required": False},
            "original_amount": {"required": False},
        }

    def validate_base_amount(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                "El monto base debe ser un valor positivo mayor que cero."
            )
        return value

    def validate_tax_percentage(self, value):
        if value is not None:
            if value < 0 or value > 30:
                raise serializers.ValidationError("La tasa de IVA debe estar entre 0 y 30%.")
        return value

    def validate_total_amount(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                "El monto total debe ser un valor positivo mayor que cero."
            )
        return value

    def validate_category(self, value):
        if value:
            user = self.context["request"].user
            if value.user != user:
                raise serializers.ValidationError(
                    "La categoría no pertenece al usuario autenticado."
                )
        return value

    def validate(self, data):
        transaction_type = data.get("type")
        origin_account = data.get("origin_account")
        destination_account = data.get("destination_account")
        category = data.get("category")
        user = self.context["request"].user

        if not user or not user.is_authenticated:
            raise serializers.ValidationError(
                "El usuario debe estar autenticado para crear una transacción."
            )

        base_amount = data.get("base_amount")
        total_amount = data.get("total_amount")
        tax_percentage = data.get("tax_percentage")

        if base_amount is not None:
            if isinstance(base_amount, (float, Decimal)):
                data["base_amount"] = int(Decimal(str(base_amount)) * Decimal("100"))
            elif isinstance(base_amount, str):
                try:
                    decimal_val = Decimal(base_amount)
                    if "." in base_amount:
                        data["base_amount"] = int(decimal_val * Decimal("100"))
                    else:
                        data["base_amount"] = int(decimal_val)
                except (ValueError, TypeError):
                    pass
            elif isinstance(base_amount, int):
                data["base_amount"] = base_amount

        if total_amount is not None:
            if isinstance(total_amount, (float, Decimal)):
                data["total_amount"] = int(Decimal(str(total_amount)) * Decimal("100"))
            elif isinstance(total_amount, str):
                try:
                    decimal_val = Decimal(total_amount)
                    if "." in total_amount:
                        data["total_amount"] = int(decimal_val * Decimal("100"))
                    else:
                        data["total_amount"] = int(decimal_val)
                except (ValueError, TypeError):
                    pass
            elif isinstance(total_amount, int):
                data["total_amount"] = total_amount

        base_amount = data.get("base_amount")
        total_amount = data.get("total_amount")

        has_base = base_amount is not None
        has_total = total_amount is not None
        has_tax = tax_percentage is not None

        if has_base and has_total:
            raise serializers.ValidationError(
                {
                    "base_amount": "No se puede proporcionar base_amount y total_amount simultáneamente. Use uno u otro.",
                    "total_amount": "No se puede proporcionar base_amount y total_amount simultáneamente. Use uno u otro.",
                }
            )

        if has_total and has_tax:
            tax_rate = Decimal(str(tax_percentage)) / Decimal("100")
            calculated_base = Decimal(str(total_amount)) / (Decimal("1") + tax_rate)
            calculated_taxed = Decimal(str(total_amount)) - calculated_base

            data["base_amount"] = int(calculated_base)
            data["taxed_amount"] = int(calculated_taxed)
            original_total = int(total_amount)
            data.pop("total_amount", None)
            data["_original_total_for_validation"] = original_total

        elif has_base and has_tax:
            pass

        elif has_base or has_total:
            if has_tax:
                raise serializers.ValidationError(
                    {
                        "tax_percentage": "Para usar IVA, debe proporcionar total_amount junto con tax_percentage (modo nuevo) o base_amount junto con tax_percentage (modo tradicional)."
                    }
                )
            if has_total:
                data["base_amount"] = total_amount
                data["taxed_amount"] = 0

        if not has_base and not has_total:
            raise serializers.ValidationError(
                {
                    "base_amount": "Debe proporcionar base_amount o total_amount.",
                    "total_amount": "Debe proporcionar base_amount o total_amount.",
                }
            )

        if transaction_type == 3:
            if not destination_account:
                raise serializers.ValidationError(
                    {"destination_account": "La cuenta destino es obligatoria para transferencias."}
                )

            if origin_account and destination_account:
                if origin_account.id == destination_account.id:
                    raise serializers.ValidationError(
                        {
                            "destination_account": "La cuenta destino debe ser diferente a la cuenta origen."
                        }
                    )

            # Las transferencias NO deben tener categoría
            if category:
                raise serializers.ValidationError(
                    {"category": "Las transferencias no deben tener categoría asignada."}
                )

        # Validaciones para ingresos y gastos (type = 1 o 2)
        elif transaction_type in [1, 2]:  # Income o Expense
            if not category:
                raise serializers.ValidationError(
                    {"category": "La categoría es obligatoria para ingresos y gastos."}
                )

            # Validar que la categoría sea del tipo correcto
            if category:
                if transaction_type == 1 and category.type != Category.INCOME:
                    raise serializers.ValidationError(
                        {
                            "category": 'La categoría debe ser de tipo "Ingreso" para transacciones de ingreso.'
                        }
                    )
                elif transaction_type == 2 and category.type != Category.EXPENSE:
                    raise serializers.ValidationError(
                        {
                            "category": 'La categoría debe ser de tipo "Gasto" para transacciones de gasto.'
                        }
                    )

            # Ingresos y gastos NO deben tener cuenta destino
            if destination_account:
                raise serializers.ValidationError(
                    {
                        "destination_account": "La cuenta destino solo debe proporcionarse para transferencias."
                    }
                )

        if transaction_type == 3 and destination_account:
            if destination_account.category == Account.CREDIT_CARD:
                capital_amount = data.get("capital_amount")
                interest_amount = data.get("interest_amount")
                total_amount = data.get("total_amount")

                # Si se especificó capital_amount, validar que capital + interest = total
                if capital_amount is not None:
                    if total_amount is None:
                        raise serializers.ValidationError(
                            {
                                "total_amount": "El monto total es requerido cuando se especifica capital_amount."
                            }
                        )

                    # Si también se especificó interest_amount, deben coincidir
                    if interest_amount is not None:
                        if capital_amount + interest_amount != total_amount:
                            raise serializers.ValidationError(
                                {
                                    "capital_amount": f"capital_amount ({capital_amount}) + interest_amount ({interest_amount}) debe ser igual a total_amount ({total_amount})."
                                }
                            )
                    # Si no se especificó interest_amount, se calculará automáticamente

                # Validar que capital_amount no sea negativo
                if capital_amount is not None and capital_amount < 0:
                    raise serializers.ValidationError(
                        {"capital_amount": "El monto de capital no puede ser negativo."}
                    )

                # Validar que interest_amount no sea negativo (si se especifica)
                if interest_amount is not None and interest_amount < 0:
                    raise serializers.ValidationError(
                        {"interest_amount": "El monto de intereses no puede ser negativo."}
                    )

        # Validar límites de cuentas ANTES de crear la transacción
        final_total = data.get("total_amount")
        if final_total is None:
            if "_original_total_for_validation" in data:
                final_total = data["_original_total_for_validation"]
            else:
                base = data.get("base_amount", 0)
                taxed = data.get("taxed_amount", 0)
                final_total = base + taxed

        if origin_account:
            final_total_pesos = (
                Decimal(str(final_total)) / Decimal("100") if final_total else Decimal("0")
            )
            TransactionSerializer._validate_account_limits(
                origin_account, final_total_pesos, transaction_type, is_decrease=True
            )

        if destination_account and transaction_type == 3:
            final_total_pesos = (
                Decimal(str(final_total)) / Decimal("100") if final_total else Decimal("0")
            )
            TransactionSerializer._validate_account_limits(
                destination_account, final_total_pesos, transaction_type, is_decrease=False
            )

        goal = data.get("goal")
        if goal:
            if transaction_type != 4:
                raise serializers.ValidationError(
                    {"goal": "Solo se pueden asignar metas a transacciones tipo Saving (type=4)."}
                )
            if goal.user != user:
                raise serializers.ValidationError(
                    {"goal": "La meta de ahorro no pertenece al usuario autenticado."}
                )

        if origin_account:
            account_currency = origin_account.currency
            transaction_currency = data.get("transaction_currency")

            if not transaction_currency:
                data["transaction_currency"] = account_currency

            if transaction_currency and transaction_currency != account_currency:
                from utils.currency_converter import CurrencyConverter

                exchange_rate = data.get("exchange_rate")
                original_amount = data.get("original_amount")

                if not exchange_rate or not original_amount:
                    raise serializers.ValidationError(
                        {
                            "transaction_currency": f"Si la moneda de la transacción ({transaction_currency}) difiere de la cuenta ({account_currency}), debe proporcionar exchange_rate y original_amount."
                        }
                    )

                try:
                    if original_amount:
                        converted_amount = CurrencyConverter.convert(
                            original_amount, transaction_currency, account_currency
                        )
                        if "base_amount" in data and data["base_amount"] != converted_amount:
                            logger.warning(
                                f"base_amount ({data['base_amount']}) no coincide con conversión ({converted_amount}). "
                                f"Usando conversión automática."
                            )
                        data["base_amount"] = converted_amount
                except ValueError as e:
                    raise serializers.ValidationError(
                        {"transaction_currency": f"Error en conversión de moneda: {str(e)}"}
                    )

            if goal and transaction_type == 4:
                if goal.currency != account_currency:
                    raise serializers.ValidationError(
                        {
                            "goal": f"La moneda de la meta ({goal.currency}) debe coincidir con la moneda de la cuenta ({account_currency})."
                        }
                    )

        if transaction_type == 3 and origin_account and destination_account:
            if origin_account.currency != destination_account.currency:
                raise serializers.ValidationError(
                    {
                        "destination_account": f"Las cuentas de origen y destino deben tener la misma moneda. "
                        f"Origen: {origin_account.currency}, Destino: {destination_account.currency}"
                    }
                )

        return data

    @staticmethod
    def _validate_account_limits(account, amount, transaction_type, is_decrease=True):
        from decimal import Decimal

        account = Account.objects.get(pk=account.pk)
        current_balance = account.current_balance
        amount_decimal = Decimal(str(amount)) if not isinstance(amount, Decimal) else amount

        if is_decrease:
            new_balance = current_balance - amount_decimal
        else:
            new_balance = current_balance + amount_decimal

        # Validar según el tipo de cuenta
        if account.account_type == Account.ASSET:
            # Cuentas de activo no pueden quedar en negativo
            if new_balance < 0:
                raise serializers.ValidationError(
                    {
                        "origin_account"
                        if is_decrease
                        else "destination_account": f"No se puede realizar esta transacción. El saldo resultante sería negativo (${new_balance:,.2f}). "
                        f"Saldo actual: ${current_balance:,.2f}, Monto: ${amount_decimal:,.2f}"
                    }
                )

        elif account.account_type == Account.LIABILITY:
            # Para tarjetas de crédito, validar límite de crédito
            if account.category == Account.CREDIT_CARD:
                if account.credit_limit is not None:
                    current_debt = abs(current_balance)
                    new_debt = abs(new_balance) if new_balance < 0 else Decimal("0.00")

                    if is_decrease and new_debt > account.credit_limit:
                        available_credit = account.credit_limit - current_debt
                        raise serializers.ValidationError(
                            {
                                "origin_account": f"No se puede realizar esta transacción. Se excedería el límite de crédito. "
                                f"Límite: ${account.credit_limit:,.2f}, Deuda actual: ${current_debt:,.2f}, "
                                f"Crédito disponible: ${available_credit:,.2f}, Monto: ${amount_decimal:,.2f}"
                            }
                        )

                # Las tarjetas de crédito no pueden tener saldo positivo
                if new_balance > 0:
                    raise serializers.ValidationError(
                        {
                            "origin_account"
                            if is_decrease
                            else "destination_account": "Las tarjetas de crédito no pueden tener saldo positivo."
                        }
                    )
            else:
                # Otras cuentas de pasivo no pueden tener saldo positivo
                if new_balance > 0:
                    raise serializers.ValidationError(
                        {
                            "origin_account"
                            if is_decrease
                            else "destination_account": "Las cuentas de pasivo no pueden tener saldo positivo."
                        }
                    )

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        validated_data.pop("_original_total_for_validation", None)
        return Transaction.objects.create(**validated_data)


class TransactionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "origin_account",
            "destination_account",
            "category",
            "type",
            "base_amount",
            "tax_percentage",
            "taxed_amount",
            "gmf_amount",
            "capital_amount",
            "interest_amount",
            "total_amount",
            "date",
            "tag",
            "note",
            "description",
            "category",
        ]
        extra_kwargs = {
            "tag": {"required": False},
            "note": {"required": False},
            "description": {"required": False},
            "category": {"required": False},
            "gmf_amount": {"read_only": True},
            "capital_amount": {"required": False},
            "interest_amount": {"required": False},
            "base_amount": {"required": False},
            "tax_percentage": {"required": False},
            "total_amount": {"required": False},
            "taxed_amount": {"read_only": True},
        }

    def validate_base_amount(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                "El monto base debe ser un valor positivo mayor que cero."
            )
        return value

    def validate_tax_percentage(self, value):
        if value is not None:
            if value < 0 or value > 30:
                raise serializers.ValidationError("La tasa de IVA debe estar entre 0 y 30%.")
        return value

    def validate_total_amount(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError(
                "El monto total debe ser un valor positivo mayor que cero."
            )
        return value

    def validate_category(self, value):
        if value:
            if hasattr(self, "instance") and self.instance:
                user = self.instance.user
            else:
                user = self.context["request"].user

            if value.user != user:
                raise serializers.ValidationError(
                    "La categoría no pertenece al usuario autenticado."
                )
        return value

    def validate(self, data):
        transaction_type = data.get(
            "type", self.instance.type if hasattr(self, "instance") and self.instance else None
        )
        origin_account = data.get(
            "origin_account",
            self.instance.origin_account if hasattr(self, "instance") and self.instance else None,
        )
        destination_account = data.get(
            "destination_account",
            self.instance.destination_account
            if hasattr(self, "instance") and self.instance
            else None,
        )
        category = data.get(
            "category",
            self.instance.category if hasattr(self, "instance") and self.instance else None,
        )

        base_amount = data.get("base_amount")
        total_amount = data.get("total_amount")
        tax_percentage = data.get("tax_percentage")

        if base_amount is not None:
            if isinstance(base_amount, (float, Decimal)):
                data["base_amount"] = int(Decimal(str(base_amount)) * Decimal("100"))
            elif isinstance(base_amount, str):
                try:
                    decimal_val = Decimal(base_amount)
                    if "." in base_amount:
                        data["base_amount"] = int(decimal_val * Decimal("100"))
                    else:
                        data["base_amount"] = int(decimal_val)
                except (ValueError, TypeError):
                    pass
            elif isinstance(base_amount, int):
                data["base_amount"] = base_amount

        if total_amount is not None:
            if isinstance(total_amount, (float, Decimal)):
                data["total_amount"] = int(Decimal(str(total_amount)) * Decimal("100"))
            elif isinstance(total_amount, str):
                try:
                    decimal_val = Decimal(total_amount)
                    if "." in total_amount:
                        data["total_amount"] = int(decimal_val * Decimal("100"))
                    else:
                        data["total_amount"] = int(decimal_val)
                except (ValueError, TypeError):
                    pass
            elif isinstance(total_amount, int):
                data["total_amount"] = total_amount

        # Actualizar las variables después de la conversión
        base_amount = data.get("base_amount")
        total_amount = data.get("total_amount")

        # Si no se proporcionan en data, usar valores de la instancia actual
        if base_amount is None and hasattr(self, "instance") and self.instance:
            base_amount = self.instance.base_amount
        if total_amount is None and hasattr(self, "instance") and self.instance:
            total_amount = self.instance.total_amount
        if tax_percentage is None and hasattr(self, "instance") and self.instance:
            tax_percentage = self.instance.tax_percentage

        # Detectar modo de cálculo
        has_base = base_amount is not None
        has_total = total_amount is not None
        has_tax = tax_percentage is not None

        # Validar que no se envíen ambos modos simultáneamente (solo si ambos están en data)
        if "base_amount" in data and "total_amount" in data:
            raise serializers.ValidationError(
                {
                    "base_amount": "No se puede proporcionar base_amount y total_amount simultáneamente. Use uno u otro.",
                    "total_amount": "No se puede proporcionar base_amount y total_amount simultáneamente. Use uno u otro.",
                }
            )

        # Modo nuevo (HU-15): total_amount + tax_percentage → calcular base_amount
        if has_total and has_tax and ("total_amount" in data or "tax_percentage" in data):
            # Calcular base_amount desde total_amount
            # base = total / (1 + tax_percentage/100)
            tax_rate = Decimal(str(tax_percentage)) / Decimal("100")
            calculated_base = Decimal(str(total_amount)) / (Decimal("1") + tax_rate)
            calculated_taxed = Decimal(str(total_amount)) - calculated_base

            # Convertir a enteros (centavos)
            data["base_amount"] = int(calculated_base)
            data["taxed_amount"] = int(calculated_taxed)
            # Guardar el total original para validaciones (sin GMF aún)
            original_total = int(total_amount)
            # NO incluir total_amount en data, el modelo lo calculará incluyendo GMF
            data.pop("total_amount", None)
            # Guardar temporalmente para validaciones
            data["_original_total_for_validation"] = original_total

        # Modo tradicional: base_amount + tax_percentage → calcular taxed_amount y total_amount
        elif has_base and has_tax and ("base_amount" in data or "tax_percentage" in data):
            # El modelo calculará taxed_amount y total_amount en save()
            pass

        # Modo sin impuestos: solo base_amount o total_amount
        elif (has_base or has_total) and ("base_amount" in data or "total_amount" in data):
            if has_tax and "tax_percentage" in data:
                raise serializers.ValidationError(
                    {
                        "tax_percentage": "Para usar IVA, debe proporcionar total_amount junto con tax_percentage (modo nuevo) o base_amount junto con tax_percentage (modo tradicional)."
                    }
                )
            # Si solo viene base_amount, el modelo calculará total_amount sin impuestos
            # Si solo viene total_amount, asumimos que es el total final (sin IVA)
            if has_total and "total_amount" in data:
                data["base_amount"] = total_amount
                data["taxed_amount"] = 0

        if transaction_type == 3:  # Transferencia
            if not destination_account:
                raise serializers.ValidationError(
                    {"destination_account": "La cuenta destino es obligatoria para transferencias."}
                )

            # Validar que las cuentas origen y destino sean diferentes
            if origin_account and destination_account:
                if origin_account.id == destination_account.id:
                    raise serializers.ValidationError(
                        {
                            "destination_account": "La cuenta destino debe ser diferente a la cuenta origen."
                        }
                    )

            # Las transferencias NO deben tener categoría
            if category:
                raise serializers.ValidationError(
                    {"category": "Las transferencias no deben tener categoría asignada."}
                )

        # Validaciones para ingresos y gastos (type = 1 o 2)
        elif transaction_type in [1, 2]:  # Income o Expense
            if not category:
                raise serializers.ValidationError(
                    {"category": "La categoría es obligatoria para ingresos y gastos."}
                )

            # Validar que la categoría sea del tipo correcto
            if category:
                if transaction_type == 1 and category.type != Category.INCOME:
                    raise serializers.ValidationError(
                        {
                            "category": 'La categoría debe ser de tipo "Ingreso" para transacciones de ingreso.'
                        }
                    )
                elif transaction_type == 2 and category.type != Category.EXPENSE:
                    raise serializers.ValidationError(
                        {
                            "category": 'La categoría debe ser de tipo "Gasto" para transacciones de gasto.'
                        }
                    )

            # Ingresos y gastos NO deben tener cuenta destino
            if destination_account:
                raise serializers.ValidationError(
                    {
                        "destination_account": "La cuenta destino solo debe proporcionarse para transferencias."
                    }
                )

        # Nota: La validación de límites se hace en el servicio después de revertir
        # la transacción anterior, por lo que aquí solo validamos la estructura básica

        # HU-11: Validar que goal solo se asigne a transacciones tipo Saving
        goal = data.get(
            "goal", self.instance.goal if hasattr(self, "instance") and self.instance else None
        )
        if goal:
            if transaction_type != 4:
                raise serializers.ValidationError(
                    {"goal": "Solo se pueden asignar metas a transacciones tipo Saving (type=4)."}
                )
            # Validar que la meta pertenezca al usuario
            if hasattr(self, "instance") and self.instance:
                user = self.instance.user
            else:
                user = self.context["request"].user
            if goal.user != user:
                raise serializers.ValidationError(
                    {"goal": "La meta de ahorro no pertenece al usuario autenticado."}
                )

        # Validación de monedas (similar a create)
        origin_account = data.get(
            "origin_account",
            self.instance.origin_account if hasattr(self, "instance") and self.instance else None,
        )
        if origin_account:
            account_currency = origin_account.currency
            transaction_currency = data.get(
                "transaction_currency",
                self.instance.transaction_currency
                if hasattr(self, "instance") and self.instance
                else None,
            )

            if transaction_currency and transaction_currency != account_currency:
                exchange_rate = data.get("exchange_rate")
                original_amount = data.get("original_amount")

                if not exchange_rate or not original_amount:
                    raise serializers.ValidationError(
                        {
                            "transaction_currency": f"Si la moneda de la transacción ({transaction_currency}) difiere de la cuenta ({account_currency}), debe proporcionar exchange_rate y original_amount."
                        }
                    )

        return data

    @staticmethod
    def _validate_account_limits(account, amount, transaction_type, is_decrease=True):
        """
        Validar que una transacción no exceda los límites de una cuenta

        Args:
            account: Instancia de Account
            amount: Monto de la transacción
            transaction_type: Tipo de transacción (1=Income, 2=Expense, 3=Transfer)
            is_decrease: True si disminuye el saldo, False si lo aumenta
        """
        # Recargar la cuenta para tener el saldo actualizado
        account = Account.objects.get(pk=account.pk)
        current_balance = account.current_balance
        # amount ya viene en PESOS (Decimal) desde la llamada
        amount_decimal = Decimal(str(amount)) if not isinstance(amount, Decimal) else amount

        # Calcular el saldo resultante
        if is_decrease:
            new_balance = current_balance - amount_decimal
        else:
            new_balance = current_balance + amount_decimal

        # Validar según el tipo de cuenta
        if account.account_type == Account.ASSET:
            # Cuentas de activo no pueden quedar en negativo
            if new_balance < 0:
                raise serializers.ValidationError(
                    {
                        "origin_account"
                        if is_decrease
                        else "destination_account": f"No se puede realizar esta transacción. El saldo resultante sería negativo (${new_balance:,.2f}). "
                        f"Saldo actual: ${current_balance:,.2f}, Monto: ${amount_decimal:,.2f}"
                    }
                )

        elif account.account_type == Account.LIABILITY:
            # Para tarjetas de crédito, validar límite de crédito
            if account.category == Account.CREDIT_CARD:
                if account.credit_limit is not None:
                    current_debt = abs(current_balance)
                    new_debt = abs(new_balance) if new_balance < 0 else Decimal("0.00")

                    if is_decrease and new_debt > account.credit_limit:
                        available_credit = account.credit_limit - current_debt
                        raise serializers.ValidationError(
                            {
                                "origin_account": f"No se puede realizar esta transacción. Se excedería el límite de crédito. "
                                f"Límite: ${account.credit_limit:,.2f}, Deuda actual: ${current_debt:,.2f}, "
                                f"Crédito disponible: ${available_credit:,.2f}, Monto: ${amount_decimal:,.2f}"
                            }
                        )

                # Las tarjetas de crédito no pueden tener saldo positivo
                if new_balance > 0:
                    raise serializers.ValidationError(
                        {
                            "origin_account"
                            if is_decrease
                            else "destination_account": "Las tarjetas de crédito no pueden tener saldo positivo."
                        }
                    )
            else:
                # Otras cuentas de pasivo no pueden tener saldo positivo
                if new_balance > 0:
                    raise serializers.ValidationError(
                        {
                            "origin_account"
                            if is_decrease
                            else "destination_account": "Las cuentas de pasivo no pueden tener saldo positivo."
                        }
                    )


class TransactionDuplicateSerializer(serializers.ModelSerializer):
    """Serializer para duplicar transacciones existentes"""

    class Meta:
        model = Transaction
        fields = [
            "origin_account",
            "destination_account",
            "type",
            "base_amount",
            "tax_percentage",
            "taxed_amount",
            "gmf_amount",
            "capital_amount",
            "interest_amount",
            "total_amount",
            "date",
        ]
        extra_kwargs = {
            "gmf_amount": {"read_only": True},  # Se calcula automáticamente
            "capital_amount": {"required": False},
            "interest_amount": {"required": False},
        }

    def create(self, validated_data):
        """Crear una nueva transacción duplicando los datos proporcionados"""
        return Transaction.objects.create(**validated_data)
