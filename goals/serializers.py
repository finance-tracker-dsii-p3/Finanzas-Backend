from rest_framework import serializers

from goals.models import Goal


class GoalDetailSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    currency_display = serializers.CharField(source="get_currency_display", read_only=True)

    class Meta:
        model = Goal
        fields = [
            "id",
            "user",
            "name",
            "target_amount",
            "saved_amount",
            "date",
            "description",
            "currency",
            "currency_display",
            "progress_percentage",
            "remaining_amount",
            "is_completed",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "saved_amount",
            "progress_percentage",
            "remaining_amount",
            "is_completed",
            "created_at",
            "updated_at",
        ]

    def get_progress_percentage(self, obj):
        return obj.get_progress_percentage()

    def get_remaining_amount(self, obj):
        return obj.get_remaining_amount()

    def get_is_completed(self, obj):
        return obj.is_completed()


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = [
            "id",
            "user",
            "name",
            "target_amount",
            "saved_amount",
            "date",
            "description",
            "currency",
        ]
        read_only_fields = ["id", "user", "saved_amount"]

    def validate_target_amount(self, value):
        if value <= 0:
            msg = "El monto objetivo debe ser un valor positivo mayor que cero."
            raise serializers.ValidationError(msg)
        return value

    def validate(self, data):
        user = self.context["request"].user

        if not user or not user.is_authenticated:
            msg = "El usuario debe estar autenticado para crear una meta."
            raise serializers.ValidationError(msg)
        return data

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["user"] = user
        if "saved_amount" not in validated_data:
            validated_data["saved_amount"] = 0
        return Goal.objects.create(**validated_data)


class GoalUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = [
            "name",
            "target_amount",
            "date",
            "description",
            "currency",
        ]

    def validate_target_amount(self, value):
        if value <= 0:
            msg = "El monto objetivo debe ser un valor positivo mayor que cero."
            raise serializers.ValidationError(msg)
        return value
