from rest_framework import serializers
from transactions.models import Transaction


class TransactionDetailSerializer(serializers.ModelSerializer):
    """Serializer para ver detalle completo de una transacción"""

    class Meta:
        model = Transaction
        fields = [
            "id",
            "user",
            "origin_account",
            "destination_account",
            "type",
            "base_amount",
            "tax_percentage",
            "taxed_amount",
            "total_amount",
            "date",
        ]
        read_only_fields = [
            "id",
            "user",
            "origin_account",
            "destination_account",
            "type",
            "base_amount",
            "tax_percentage",
            "taxed_amount",
            "total_amount",
            "date",
        ]


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer para la creación de transacciones"""
    
    class Meta:
        model = Transaction
        fields = [
            'id',
            'user',
            'origin_account',
            'destination_account',
            'type',
            'base_amount',
            'tax_percentage',
            'taxed_amount',
            'total_amount',
            'date'
        ]
        read_only_fields = ['id', 'user']

    def validate_amount(self, value):
        """Validar que el monto sea positivo"""
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser un valor positivo mayor que cero.")
        return value
    
    def validate(self, data):
        """Validar lógica específica para transferencias"""
        transaction_type = data.get('type')
        destination_account = data.get('destination_account')
        user = self.context['request'].user
        
        if not user or not user.is_authenticated:
            raise serializers.ValidationError("El usuario debe estar autenticado para crear una transacción.")

        if transaction_type == 3:  # Transferencia
            if not destination_account:
                raise serializers.ValidationError("La cuenta destino es obligatoria para transferencias.")
    
        if transaction_type != 3 and destination_account:
            raise serializers.ValidationError("La cuenta destino solo debe proporcionarse para transferencias.")
        
        return data
    
    def create(self, validated_data):
        """Crear transacción asignando el usuario del request"""
        user = self.context['request'].user
        validated_data['user'] = user
        return Transaction.objects.create(**validated_data)


class TransactionUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar transacciones existentes"""
    
    class Meta:
        model = Transaction
        fields = [
            'origin_account',
            'destination_account',
            'type',
            'base_amount',
            'tax_percentage',
            'taxed_amount',
            'total_amount',
            'date'
        ]
    
    def validate_amount(self, value):
        """Validar que el monto sea positivo"""
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser un valor positivo mayor que cero.")
        return value
    
    def validate(self, data):
        """Validar lógica específica para transferencias"""
        transaction_type = data.get('type', self.instance.type)
        destination_account = data.get('destination_account', self.instance.destination_account)
        
        if transaction_type == 3:  # Transferencia
            if not destination_account:
                raise serializers.ValidationError("La cuenta destino es obligatoria para transferencias.")
    
        if transaction_type != 3 and destination_account:
            raise serializers.ValidationError("La cuenta destino solo debe proporcionarse para transferencias.")
        

class TransactionDuplicateSerializer(serializers.ModelSerializer):
    """Serializer para duplicar transacciones existentes"""
    
    class Meta:
        model = Transaction
        fields = [
            'origin_account',
            'destination_account',
            'type',
            'base_amount',
            'tax_percentage',
            'taxed_amount',
            'total_amount',
            'date'
        ]
    
    def create(self, validated_data):
        """Crear una nueva transacción duplicando los datos proporcionados"""
        return Transaction.objects.create(**validated_data)