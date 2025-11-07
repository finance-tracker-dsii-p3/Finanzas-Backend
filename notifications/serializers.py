from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer básico para notificaciones - adaptado para proyecto financiero
    """
    recipient_name = serializers.CharField(source='user.get_full_name', read_only=True)
    recipient_username = serializers.CharField(source='user.username', read_only=True)
    is_read = serializers.BooleanField(source='read', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    # Permitir creación desde API para admins
    user = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(), 
        required=False, 
        write_only=True
    )
    notification_type = serializers.ChoiceField(
        choices=Notification.TYPE_CHOICES, 
        write_only=True, 
        required=True
    )
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message', 'read', 'is_read', 
            'created_at', 'recipient_name', 'recipient_username', 'user_id', 
            'user_name', 'user', 'related_object_id'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        """Crear notificación asignando usuario apropiado"""
        request = self.context.get('request') if self.context else None
        user = validated_data.pop('user', None)
        
        if user is None and request is not None:
            user = request.user
            
        return Notification.objects.create(user=user, **validated_data)


class SystemAlertSerializer(serializers.ModelSerializer):
    """
    Serializer para alertas del sistema - versión simplificada
    """
    recipient_name = serializers.CharField(source='user.get_full_name', read_only=True)
    recipient_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type',
            'read', 'created_at', 'recipient_name', 'recipient_username',
            'related_object_id'
        ]
        read_only_fields = ['created_at']