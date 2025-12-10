from rest_framework import serializers
from credit_cards.models import InstallmentPlan, InstallmentPayment
from accounts.models import Account
from categories.models import Category
from transactions.models import Transaction


class InstallmentPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstallmentPayment
        fields = [
            "id",
            "installment_number",
            "due_date",
            "installment_amount",
            "principal_amount",
            "interest_amount",
            "status",
            "payment_date",
            "notes",
        ]
        read_only_fields = [
            "status",
            "payment_date",
            "installment_amount",
            "principal_amount",
            "interest_amount",
        ]


class InstallmentPlanSerializer(serializers.ModelSerializer):
    payments = InstallmentPaymentSerializer(many=True, read_only=True)
    credit_card_account_name = serializers.CharField(
        source="credit_card_account.name", read_only=True
    )
    financing_category_name = serializers.CharField(
        source="financing_category.name", read_only=True
    )

    class Meta:
        model = InstallmentPlan
        fields = [
            "id",
            "user",
            "credit_card_account",
            "credit_card_account_name",
            "purchase_transaction",
            "description",
            "purchase_amount",
            "number_of_installments",
            "interest_rate",
            "installment_amount",
            "total_interest",
            "total_principal",
            "total_amount",
            "start_date",
            "status",
            "financing_category",
            "financing_category_name",
            "payments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "installment_amount",
            "status",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):
        user = self.context["request"].user
        credit_card = data.get("credit_card_account")
        purchase_tx = data.get("purchase_transaction")
        financing_category = data.get("financing_category")

        if credit_card and credit_card.user != user:
            raise serializers.ValidationError(
                {"credit_card_account": "La tarjeta no pertenece al usuario."}
            )
        if credit_card and credit_card.category != Account.CREDIT_CARD:
            raise serializers.ValidationError(
                {"credit_card_account": "Debe ser una cuenta de tarjeta de crédito."}
            )

        if purchase_tx and purchase_tx.user != user:
            raise serializers.ValidationError(
                {"purchase_transaction": "La transacción no pertenece al usuario."}
            )
        if purchase_tx and purchase_tx.origin_account_id != (
            credit_card.id if credit_card else None
        ):
            raise serializers.ValidationError(
                {"purchase_transaction": "La compra debe haberse hecho con la tarjeta indicada."}
            )
        if purchase_tx and purchase_tx.type != 2:
            raise serializers.ValidationError(
                {"purchase_transaction": "La transacción debe ser un gasto (type=2)."}
            )

        if financing_category:
            if financing_category.user != user:
                raise serializers.ValidationError(
                    {"financing_category": "La categoría no pertenece al usuario."}
                )
            if financing_category.type != Category.EXPENSE:
                raise serializers.ValidationError(
                    {"financing_category": "Debe ser categoría de gasto."}
                )

        return data

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        return InstallmentPlan.objects.create(**validated_data)


class InstallmentPlanCreateSerializer(serializers.Serializer):
    credit_card_account_id = serializers.IntegerField()
    purchase_transaction_id = serializers.IntegerField()
    financing_category_id = serializers.IntegerField()
    description = serializers.CharField(required=False, allow_blank=True)
    number_of_installments = serializers.IntegerField(min_value=1)
    interest_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    start_date = serializers.DateField(required=False)

    def validate(self, data):
        user = self.context["request"].user
        try:
            credit_card = Account.objects.get(id=data["credit_card_account_id"], user=user)
        except Account.DoesNotExist:
            raise serializers.ValidationError({"credit_card_account_id": "Tarjeta no encontrada."})
        if credit_card.category != Account.CREDIT_CARD:
            raise serializers.ValidationError(
                {"credit_card_account_id": "Debe ser una tarjeta de crédito."}
            )

        try:
            purchase_tx = Transaction.objects.get(id=data["purchase_transaction_id"], user=user)
        except Transaction.DoesNotExist:
            raise serializers.ValidationError(
                {"purchase_transaction_id": "Transacción no encontrada."}
            )
        if purchase_tx.origin_account_id != credit_card.id:
            raise serializers.ValidationError(
                {"purchase_transaction_id": "La compra debe ser de esta tarjeta."}
            )
        if purchase_tx.type != 2:
            raise serializers.ValidationError(
                {"purchase_transaction_id": "Debe ser un gasto (type=2)."}
            )

        try:
            financing_category = Category.objects.get(id=data["financing_category_id"], user=user)
        except Category.DoesNotExist:
            raise serializers.ValidationError({"financing_category_id": "Categoría no encontrada."})
        if financing_category.type != Category.EXPENSE:
            raise serializers.ValidationError(
                {"financing_category_id": "Debe ser categoría de gasto."}
            )

        data["credit_card"] = credit_card
        data["purchase_tx"] = purchase_tx
        data["financing_category_obj"] = financing_category
        return data


class InstallmentPaymentRecordSerializer(serializers.Serializer):
    installment_number = serializers.IntegerField(min_value=1)
    payment_date = serializers.DateField()
    source_account_id = serializers.IntegerField()
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        user = self.context["request"].user
        plan = self.context.get("plan")
        try:
            source_account = Account.objects.get(id=data["source_account_id"], user=user)
        except Account.DoesNotExist:
            raise serializers.ValidationError(
                {"source_account_id": "Cuenta de origen no encontrada."}
            )
        if source_account.currency != plan.credit_card_account.currency:
            raise serializers.ValidationError(
                {"source_account_id": "Las cuentas deben tener la misma moneda."}
            )
        data["source_account"] = source_account
        return data
