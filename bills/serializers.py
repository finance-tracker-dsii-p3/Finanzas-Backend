"""
Serializers para gestión de facturas personales
"""

from rest_framework import serializers
from bills.models import Bill, BillReminder
from accounts.models import Account
from categories.models import Category
from transactions.models import Transaction


class BillSerializer(serializers.ModelSerializer):
    """Serializer principal para facturas"""
    
    # Campos calculados (read-only)
    days_until_due = serializers.IntegerField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    is_near_due = serializers.BooleanField(read_only=True)
    is_paid = serializers.BooleanField(read_only=True)
    
    # Información anidada de relaciones
    suggested_account_info = serializers.SerializerMethodField()
    category_info = serializers.SerializerMethodField()
    payment_info = serializers.SerializerMethodField()
    
    # Formato de moneda
    amount_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = Bill
        fields = [
            "id",
            "provider",
            "amount",
            "amount_formatted",
            "due_date",
            "suggested_account",
            "suggested_account_info",
            "category",
            "category_info",
            "status",
            "payment_transaction",
            "payment_info",
            "reminder_days_before",
            "description",
            "is_recurring",
            "days_until_due",
            "is_overdue",
            "is_near_due",
            "is_paid",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "payment_transaction", "created_at", "updated_at"]
    
    def get_amount_formatted(self, obj):
        """Formato de moneda COP"""
        return f"${obj.amount:,.0f}"
    
    def get_suggested_account_info(self, obj):
        """Información de la cuenta sugerida"""
        if obj.suggested_account:
            return {
                "id": obj.suggested_account.id,
                "name": obj.suggested_account.name,
                "bank_name": obj.suggested_account.bank_name,
                "current_balance": float(obj.suggested_account.current_balance),
            }
        return None
    
    def get_category_info(self, obj):
        """Información de la categoría"""
        if obj.category:
            return {
                "id": obj.category.id,
                "name": obj.category.name,
                "color": obj.category.color,
                "icon": obj.category.icon,
            }
        return None
    
    def get_payment_info(self, obj):
        """Información del pago realizado"""
        if obj.payment_transaction:
            return {
                "id": obj.payment_transaction.id,
                "date": obj.payment_transaction.date,
                "amount": float(obj.payment_transaction.base_amount) / 100,  # Convertir de centavos
                "account": obj.payment_transaction.origin_account.name,
            }
        return None
    
    def validate_suggested_account(self, value):
        """Validar que la cuenta pertenezca al usuario"""
        request = self.context.get("request")
        if value and request and value.user != request.user:
            raise serializers.ValidationError("La cuenta sugerida debe pertenecerte")
        return value
    
    def validate_category(self, value):
        """Validar que la categoría pertenezca al usuario"""
        request = self.context.get("request")
        if value and request and value.user != request.user:
            raise serializers.ValidationError("La categoría debe pertenecerte")
        return value
    
    def validate_amount(self, value):
        """Validar que el monto sea positivo"""
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a cero")
        return value


class BillPaymentSerializer(serializers.Serializer):
    """Serializer para registrar el pago de una factura"""
    
    account_id = serializers.IntegerField(
        required=True,
        help_text="ID de la cuenta desde la cual se realiza el pago"
    )
    
    payment_date = serializers.DateField(
        required=True,
        help_text="Fecha del pago"
    )
    
    notes = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text="Notas adicionales sobre el pago"
    )
    
    def validate_account_id(self, value):
        """Validar que la cuenta exista y pertenezca al usuario"""
        request = self.context.get("request")
        if not request:
            raise serializers.ValidationError("Contexto de request requerido")
        
        try:
            account = Account.objects.get(id=value, user=request.user)
        except Account.DoesNotExist:
            raise serializers.ValidationError("La cuenta no existe o no te pertenece")
        
        return value


class BillReminderSerializer(serializers.ModelSerializer):
    """Serializer para recordatorios de facturas"""
    
    # Información de la factura
    bill_info = serializers.SerializerMethodField()
    reminder_type_display = serializers.CharField(
        source="get_reminder_type_display",
        read_only=True
    )
    
    class Meta:
        model = BillReminder
        fields = [
            "id",
            "bill",
            "bill_info",
            "reminder_type",
            "reminder_type_display",
            "message",
            "is_read",
            "read_at",
            "created_at",
        ]
        read_only_fields = ["created_at", "read_at"]
    
    def get_bill_info(self, obj):
        """Información resumida de la factura"""
        return {
            "id": obj.bill.id,
            "provider": obj.bill.provider,
            "amount": float(obj.bill.amount),
            "amount_formatted": f"${obj.bill.amount:,.0f}",
            "due_date": obj.bill.due_date,
            "status": obj.bill.status,
        }


class BillListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de facturas"""
    
    amount_formatted = serializers.SerializerMethodField()
    days_until_due = serializers.IntegerField(read_only=True)
    is_paid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Bill
        fields = [
            "id",
            "provider",
            "amount",
            "amount_formatted",
            "due_date",
            "status",
            "days_until_due",
            "is_paid",
            "is_recurring",
            "created_at",
        ]
    
    def get_amount_formatted(self, obj):
        return f"${obj.amount:,.0f}"
