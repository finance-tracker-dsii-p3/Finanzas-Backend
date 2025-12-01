from rest_framework import serializers
from .models import ExportJob
from users.models import User


class ExportJobSerializer(serializers.ModelSerializer):
    """
    Serializer para trabajos de exportación - versión simplificada
    """

    requested_by_name = serializers.CharField(source="requested_by.get_full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    export_type_display = serializers.CharField(source="get_export_type_display", read_only=True)
    format_display = serializers.CharField(source="get_format_display", read_only=True)
    file_url = serializers.SerializerMethodField()
    file_size_mb = serializers.SerializerMethodField()

    class Meta:
        model = ExportJob
        fields = [
            "id",
            "title",
            "export_type",
            "export_type_display",
            "format",
            "format_display",
            "status",
            "status_display",
            "start_date",
            "end_date",
            "user_ids",
            "file",
            "file_url",
            "file_size",
            "file_size_mb",
            "requested_by",
            "requested_by_name",
            "created_at",
            "updated_at",
            "completed_at",
            "error_message",
        ]
        read_only_fields = [
            "id",
            "status",
            "file",
            "file_size",
            "requested_by",
            "created_at",
            "updated_at",
            "completed_at",
            "error_message",
        ]

    def get_file_url(self, obj):
        """Obtiene la URL del archivo si existe"""
        if obj.file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None

    def get_file_size_mb(self, obj):
        """Convierte el tamaño del archivo a MB"""
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return None


class UserExportSerializer(serializers.ModelSerializer):
    """
    Serializer para exportar datos de usuarios - versión simplificada
    """

    full_name = serializers.CharField(source="get_full_name", read_only=True)
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    is_verified_display = serializers.SerializerMethodField()
    is_active_display = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "identification",
            "phone",
            "role",
            "role_display",
            "is_verified",
            "is_verified_display",
            "is_active",
            "is_active_display",
            "date_joined",
            "last_login",
        ]

    def get_is_verified_display(self, obj):
        """Convierte el booleano a texto"""
        return "Sí" if obj.is_verified else "No"

    def get_is_active_display(self, obj):
        """Convierte el booleano a texto"""
        return "Sí" if obj.is_active else "No"
