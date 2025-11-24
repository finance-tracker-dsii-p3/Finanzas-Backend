from rest_framework import serializers
from decimal import Decimal
from .models import Account, AccountOption


class AccountListSerializer(serializers.ModelSerializer):
    """Serializer para listar cuentas - solo campos esenciales"""
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    credit_card_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Account
        fields = [
            'id', 'name', 'bank_name', 'account_number', 'account_type', 'account_type_display',
            'category', 'category_display', 'currency', 'currency_display',
            'current_balance', 'is_active', 'gmf_exempt',
            'expiration_date', 'credit_limit', 'credit_card_details'
        ]
    
    def get_credit_card_details(self, obj):
        """Obtener detalles de tarjeta de crédito si aplica"""
        if obj.category == Account.CREDIT_CARD:
            from .services import AccountService
            return AccountService.get_credit_card_details(obj)
        return None


class AccountDetailSerializer(serializers.ModelSerializer):
    """Serializer para ver detalle completo de una cuenta"""
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    credit_card_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Account
        fields = [
            'id', 'name', 'bank_name', 'account_number', 'description', 'account_type', 'account_type_display',
            'category', 'category_display', 'currency', 'currency_display',
            'current_balance', 'is_active', 'gmf_exempt',
            'expiration_date', 'credit_limit', 'credit_card_details',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_credit_card_details(self, obj):
        """Obtener detalles de tarjeta de crédito si aplica"""
        if obj.category == Account.CREDIT_CARD:
            from .services import AccountService
            return AccountService.get_credit_card_details(obj)
        return None


class AccountCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear nuevas cuentas"""
    
    class Meta:
        model = Account
        fields = [
            'name', 'bank_name', 'account_number', 'account_type', 'category', 'currency',
            'current_balance', 'description', 'is_active',
            'gmf_exempt', 'expiration_date', 'credit_limit'
        ]
        extra_kwargs = {
            'current_balance': {'required': False, 'default': Decimal('0.00')},
            'description': {'required': False},
            'bank_name': {'required': False},
            'account_number': {'required': False},
            'is_active': {'required': False, 'default': True},
            'gmf_exempt': {'required': False, 'default': False},
            'expiration_date': {'required': False},
            'credit_limit': {'required': False}
        }
    
    def validate(self, attrs):
        category = attrs.get('category')
        account_type = attrs.get('account_type')
        current_balance = attrs.get('current_balance', Decimal('0.00'))
        expiration_date = attrs.get('expiration_date')
        credit_limit = attrs.get('credit_limit')
        
        if category == Account.CREDIT_CARD:
            attrs['account_type'] = Account.LIABILITY
            if current_balance > 0:
                raise serializers.ValidationError({
                    'current_balance': 'Las tarjetas de crédito no pueden tener saldo positivo.'
                })
            # Validar que credit_limit sea positivo si se proporciona
            if credit_limit is not None and credit_limit <= 0:
                raise serializers.ValidationError({
                    'credit_limit': 'El límite de crédito debe ser mayor a cero.'
                })
        else:
            # Si no es tarjeta de crédito, no debería tener estos campos
            if expiration_date is not None:
                raise serializers.ValidationError({
                    'expiration_date': 'La fecha de vencimiento solo aplica para tarjetas de crédito.'
                })
            if credit_limit is not None:
                raise serializers.ValidationError({
                    'credit_limit': 'El límite de crédito solo aplica para tarjetas de crédito.'
                })
        
        if account_type == Account.LIABILITY and current_balance > 0:
            raise serializers.ValidationError({
                'current_balance': 'Las cuentas de pasivo deben tener saldo negativo o cero.'
            })
        
        if account_type == Account.ASSET and current_balance < 0:
            raise serializers.ValidationError({
                'current_balance': 'Las cuentas de activo no pueden tener saldo negativo.'
            })
        
        return attrs
    
    def validate_name(self, value):
        user = self.context['request'].user
        if Account.objects.filter(user=user, name__iexact=value).exists():
            raise serializers.ValidationError('Ya tienes una cuenta con este nombre.')
        return value
    
    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return Account.objects.create(**validated_data)


class AccountUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar cuentas existentes"""
    
    class Meta:
        model = Account
        fields = [
            'name', 'bank_name', 'account_number', 'account_type', 'category', 'currency', 'description', 
            'is_active', 'gmf_exempt', 'expiration_date', 'credit_limit'
        ]
        extra_kwargs = {
            'name': {'required': False},
            'bank_name': {'required': False},
            'account_number': {'required': False},
            'account_type': {'required': False},
            'category': {'required': False},
            'currency': {'required': False},
            'gmf_exempt': {'required': False},
            'expiration_date': {'required': False},
            'credit_limit': {'required': False}
        }
    
    def validate(self, attrs):
        category = attrs.get('category', self.instance.category)
        expiration_date = attrs.get('expiration_date', self.instance.expiration_date)
        credit_limit = attrs.get('credit_limit', self.instance.credit_limit)
        
        if category == Account.CREDIT_CARD:
            attrs['account_type'] = Account.LIABILITY
            # Validar credit_limit si se proporciona
            if 'credit_limit' in attrs and credit_limit is not None and credit_limit <= 0:
                raise serializers.ValidationError({
                    'credit_limit': 'El límite de crédito debe ser mayor a cero.'
                })
        else:
            # Si no es tarjeta de crédito, no debería tener estos campos
            if 'expiration_date' in attrs and expiration_date is not None:
                raise serializers.ValidationError({
                    'expiration_date': 'La fecha de vencimiento solo aplica para tarjetas de crédito.'
                })
            if 'credit_limit' in attrs and credit_limit is not None:
                raise serializers.ValidationError({
                    'credit_limit': 'El límite de crédito solo aplica para tarjetas de crédito.'
                })
        
        if 'account_type' in attrs and self.instance.current_balance != 0:
            if attrs['account_type'] != self.instance.account_type:
                raise serializers.ValidationError({
                    'account_type': 'No puedes cambiar el tipo de cuenta cuando tiene saldo.'
                })
        
        if 'currency' in attrs and self.instance.current_balance != 0:
            if attrs['currency'] != self.instance.currency:
                raise serializers.ValidationError({
                    'currency': 'No puedes cambiar la moneda cuando la cuenta tiene saldo.'
                })
        
        return attrs
    
    def validate_name(self, value):
        user = self.context['request'].user
        if Account.objects.filter(user=user, name__iexact=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError('Ya tienes una cuenta con este nombre.')
        return value


class AccountBalanceUpdateSerializer(serializers.Serializer):
    """Serializer para actualizar saldo manualmente"""
    new_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    reason = serializers.CharField(max_length=200, required=False, allow_blank=True)
    
    def validate_new_balance(self, value):
        account = self.context.get('account')
        if account:
            if account.account_type == Account.LIABILITY and value > 0:
                raise serializers.ValidationError('Las cuentas de pasivo no pueden tener saldo positivo.')
            elif account.account_type == Account.ASSET and value < 0:
                raise serializers.ValidationError('Las cuentas de activo no pueden tener saldo negativo.')
        return value


class AccountSummarySerializer(serializers.Serializer):
    """Serializer para resumen de cuentas"""
    total_assets = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_liabilities = serializers.DecimalField(max_digits=15, decimal_places=2)
    net_worth = serializers.DecimalField(max_digits=15, decimal_places=2)
    accounts_count = serializers.IntegerField()
    active_accounts_count = serializers.IntegerField()
    balances_by_currency = serializers.DictField()
    accounts_by_category = serializers.DictField()


class AccountOptionSerializer(serializers.ModelSerializer):
    """Serializer para opciones de cuentas (bancos, billeteras, etc.)"""
    option_type_display = serializers.CharField(source='get_option_type_display', read_only=True)
    
    class Meta:
        model = AccountOption
        fields = ['id', 'name', 'option_type', 'option_type_display', 'is_active', 'order']
