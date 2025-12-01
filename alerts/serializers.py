from rest_framework import serializers
from alerts.models import Alert


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = [
            "id",
            "user",
            "budget",
            "alert_type",
            "is_read",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "user",
            "budget",
        ]


class AlertReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ["is_read"]
        extra_kwargs = {
            "is_read": {"required": True},
        }
