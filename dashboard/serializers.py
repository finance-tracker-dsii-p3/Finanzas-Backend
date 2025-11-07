from rest_framework import serializers


class DashboardStatsSerializer(serializers.Serializer):
    """
    Serializer para estadísticas básicas del dashboard - adaptado para proyecto financiero
    """
    # Estadísticas de usuarios
    total_users = serializers.IntegerField(required=False)
    active_users = serializers.IntegerField(required=False)
    pending_verifications = serializers.IntegerField(required=False)
    
    # Estadísticas de notificaciones
    unread_notifications = serializers.IntegerField(required=False)
    recent_notifications = serializers.IntegerField(required=False)
    total_notifications = serializers.IntegerField(required=False)
    
    # Estadísticas de perfil
    profile_complete = serializers.BooleanField(required=False)


class MiniCardSerializer(serializers.Serializer):
    """
    Serializer para las mini cards del dashboard
    """
    title = serializers.CharField()
    value = serializers.CharField()
    icon = serializers.CharField()
    color = serializers.CharField()
    trend = serializers.CharField(required=False)
    trend_value = serializers.CharField(required=False)


class ActivitySerializer(serializers.Serializer):
    """
    Serializer para actividades recientes
    """
    id = serializers.IntegerField()
    type = serializers.CharField()
    timestamp = serializers.DateTimeField()
    description = serializers.CharField()
    read = serializers.BooleanField(required=False)


class AlertSerializer(serializers.Serializer):
    """
    Serializer para alertas
    """
    type = serializers.CharField()
    severity = serializers.CharField()
    title = serializers.CharField()
    message = serializers.CharField()
    timestamp = serializers.DateTimeField()


class DashboardDataSerializer(serializers.Serializer):
    """
    Serializer completo del dashboard - simplificado para proyecto financiero
    """
    user_info = serializers.DictField()
    stats = DashboardStatsSerializer()
    mini_cards = MiniCardSerializer(many=True)
    recent_activities = ActivitySerializer(many=True)
    alerts = AlertSerializer(many=True)
    charts_data = serializers.DictField()


