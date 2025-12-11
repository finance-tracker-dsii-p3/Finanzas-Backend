from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from alerts.models import Alert
from alerts.serializers import (
    AlertReadSerializer,
    AlertSerializer,
)


class AlertListView(generics.ListAPIView):
    """Lista de alertas del usuario autenticado con filtros"""

    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Alert.objects.filter(user=self.request.user)

        # Filter unread
        unread = self.request.GET.get("unread")
        if unread == "true":
            qs = qs.filter(is_read=False)

        # Filter by type
        alert_type = self.request.GET.get("type")
        if alert_type in ["warning", "exceeded"]:
            qs = qs.filter(alert_type=alert_type)

        return qs.order_by("-created_at")


class AlertDetailView(generics.RetrieveAPIView):
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Alert.objects.filter(user=self.request.user)


class AlertMarkAsReadView(generics.UpdateAPIView):
    """Marca una alerta como leída o no leída"""

    serializer_class = AlertReadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Alert.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        alert = self.get_object()
        serializer = self.get_serializer(alert, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {"detail": "Alerta actualizada correctamente."},
            status=status.HTTP_200_OK,
        )


class AlertMarkAllAsReadView(generics.UpdateAPIView):
    serializer_class = AlertReadSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        updated = Alert.objects.filter(user=user, is_read=False).update(is_read=True)
        return Response({"success": True, "updated_count": updated})


class AlertDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Alert.objects.filter(user=self.request.user)
