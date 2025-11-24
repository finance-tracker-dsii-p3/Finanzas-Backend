"""
Serializers para gestión de categorías
"""
from rest_framework import serializers
from .models import Category


class CategoryListSerializer(serializers.ModelSerializer):
    """Serializer para listar categorías - vista simplificada"""
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    icon_display = serializers.CharField(source='get_icon_display', read_only=True)
    usage_count = serializers.IntegerField(source='get_usage_count', read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'type', 'type_display', 'color', 'icon', 
            'icon_display', 'is_active', 'order', 'usage_count'
        ]


class CategoryDetailSerializer(serializers.ModelSerializer):
    """Serializer para ver detalle completo de una categoría"""
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    icon_display = serializers.CharField(source='get_icon_display', read_only=True)
    related_data = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'type', 'type_display', 'color', 'icon',
            'icon_display', 'is_active', 'is_default', 'order',
            'related_data', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_default', 'created_at', 'updated_at']
    
    def get_related_data(self, obj):
        """Obtener información sobre datos relacionados"""
        return obj.get_related_data()


class CategoryCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear nuevas categorías"""
    
    class Meta:
        model = Category
        fields = ['name', 'type', 'color', 'icon', 'is_active', 'order']
        extra_kwargs = {
            'color': {'required': False},
            'icon': {'required': False},
            'is_active': {'required': False},
            'order': {'required': False}
        }
    
    def validate_name(self, value):
        """Validar nombre de categoría"""
        value = value.strip().title()
        
        if len(value) < 2:
            raise serializers.ValidationError(
                'El nombre debe tener al menos 2 caracteres.'
            )
        
        if len(value) > 100:
            raise serializers.ValidationError(
                'El nombre no puede tener más de 100 caracteres.'
            )
        
        return value
    
    def validate(self, attrs):
        """Validaciones adicionales"""
        name = attrs.get('name')
        cat_type = attrs.get('type')
        user = self.context['request'].user
        
        # Verificar que el usuario esté autenticado
        if not user or not user.is_authenticated:
            raise serializers.ValidationError(
                'Debes estar autenticado para crear categorías.'
            )
        
        # Verificar duplicidad
        existing = Category.objects.filter(
            user=user,
            name__iexact=name,
            type=cat_type
        )
        
        if existing.exists():
            raise serializers.ValidationError({
                'name': f'Ya tienes una categoría de {dict(Category.TYPE_CHOICES)[cat_type]} llamada "{name}"'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Crear categoría asignando el usuario del request"""
        user = self.context['request'].user
        validated_data['user'] = user
        return Category.objects.create(**validated_data)


class CategoryUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar categorías existentes"""
    
    class Meta:
        model = Category
        fields = ['name', 'color', 'icon', 'is_active', 'order']
        extra_kwargs = {
            'name': {'required': False},
            'color': {'required': False},
            'icon': {'required': False},
            'is_active': {'required': False},
            'order': {'required': False}
        }
    
    def validate_name(self, value):
        """Validar nombre de categoría"""
        value = value.strip().title()
        
        if len(value) < 2:
            raise serializers.ValidationError(
                'El nombre debe tener al menos 2 caracteres.'
            )
        
        if len(value) > 100:
            raise serializers.ValidationError(
                'El nombre no puede tener más de 100 caracteres.'
            )
        
        return value
    
    def validate(self, attrs):
        """Validaciones adicionales"""
        instance = self.instance
        
        # No permitir edición de categorías por defecto
        if instance.is_default:
            raise serializers.ValidationError(
                'No puedes editar una categoría del sistema.'
            )
        
        # Verificar duplicidad si se cambia el nombre
        if 'name' in attrs:
            name = attrs['name']
            user = instance.user
            
            existing = Category.objects.filter(
                user=user,
                name__iexact=name,
                type=instance.type
            ).exclude(pk=instance.pk)
            
            if existing.exists():
                raise serializers.ValidationError({
                    'name': f'Ya tienes otra categoría de {instance.get_type_display()} llamada "{name}"'
                })
        
        return attrs


class CategoryReassignSerializer(serializers.Serializer):
    """Serializer para reasignar transacciones/presupuestos al eliminar categoría"""
    target_category_id = serializers.IntegerField(
        required=True,
        help_text='ID de la categoría destino para reasignar transacciones y presupuestos'
    )
    
    def validate_target_category_id(self, value):
        """Validar que la categoría destino existe y es del mismo usuario"""
        user = self.context['request'].user
        source_category = self.context['category']
        
        try:
            target_category = Category.objects.get(pk=value, user=user)
        except Category.DoesNotExist:
            raise serializers.ValidationError(
                'La categoría destino no existe o no te pertenece.'
            )
        
        # Verificar que sea del mismo tipo
        if target_category.type != source_category.type:
            raise serializers.ValidationError(
                f'La categoría destino debe ser del mismo tipo ({source_category.get_type_display()})'
            )
        
        # No puede ser la misma categoría
        if target_category.pk == source_category.pk:
            raise serializers.ValidationError(
                'No puedes reasignar a la misma categoría que estás eliminando.'
            )
        
        return value


class CategoryStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de categorías"""
    total_categories = serializers.IntegerField()
    active_categories = serializers.IntegerField()
    inactive_categories = serializers.IntegerField()
    income_categories = serializers.IntegerField()
    expense_categories = serializers.IntegerField()
    most_used = serializers.ListField()
    least_used = serializers.ListField()


class CategoryBulkOrderSerializer(serializers.Serializer):
    """Serializer para actualizar el orden de múltiples categorías"""
    categories = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField()
        ),
        help_text='Lista de {id: orden} para actualizar'
    )
    
    def validate_categories(self, value):
        """Validar que todas las categorías existen y pertenecen al usuario"""
        user = self.context['request'].user
        category_ids = [item['id'] for item in value]
        
        existing_categories = Category.objects.filter(
            pk__in=category_ids,
            user=user
        ).count()
        
        if existing_categories != len(category_ids):
            raise serializers.ValidationError(
                'Algunas categorías no existen o no te pertenecen.'
            )
        
        return value
