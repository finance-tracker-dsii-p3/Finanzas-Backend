"""
Views para preferencias de notificaciones de usuarios
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import UserNotificationPreferences
from users.serializers_preferences import UserNotificationPreferencesSerializer, TimezoneListSerializer
import pytz


class UserNotificationPreferencesViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar preferencias de notificaciones del usuario
    
    Endpoints:
    - GET /api/users/preferences/              -> Ver preferencias del usuario autenticado
    - POST /api/users/preferences/             -> Crear/actualizar preferencias
    - PATCH /api/users/preferences/            -> Actualizar preferencias parcialmente
    - GET /api/users/preferences/timezones/    -> Listar zonas horarias disponibles
    
    Nota: No requiere ID en la URL, siempre opera sobre las preferencias del usuario autenticado
    """
    
    serializer_class = UserNotificationPreferencesSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Retorna solo las preferencias del usuario autenticado"""
        return UserNotificationPreferences.objects.filter(user=self.request.user)
    
    def get_object(self):
        """
        Obtiene las preferencias del usuario autenticado
        Crea preferencias por defecto si no existen
        """
        prefs, created = UserNotificationPreferences.objects.get_or_create(
            user=self.request.user
        )
        return prefs
    
    def list(self, request, *args, **kwargs):
        """
        GET /api/users/preferences/
        Retorna las preferencias del usuario o crea unas por defecto
        """
        prefs = self.get_object()
        serializer = self.get_serializer(prefs)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """
        GET /api/users/preferences/{id}/
        Retorna las preferencias del usuario (ignora el ID y usa las del usuario autenticado)
        """
        prefs = self.get_object()
        serializer = self.get_serializer(prefs)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """
        POST /api/users/preferences/
        Crea o actualiza preferencias del usuario
        """
        prefs = self.get_object()
        
        serializer = self.get_serializer(prefs, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        """
        PUT /api/users/preferences/ o PUT /api/users/preferences/{id}/
        Actualiza preferencias del usuario (ignora el ID si se proporciona)
        """
        prefs = self.get_object()
        
        serializer = self.get_serializer(prefs, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)
    
    def partial_update(self, request, *args, **kwargs):
        """
        PATCH /api/users/preferences/ o PATCH /api/users/preferences/{id}/
        Actualiza parcialmente preferencias del usuario (ignora el ID si se proporciona)
        """
        prefs = self.get_object()
        
        serializer = self.get_serializer(prefs, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """
        DELETE no está permitido - las preferencias no se pueden eliminar
        """
        return Response(
            {"error": "No se pueden eliminar las preferencias de notificación"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    @action(detail=False, methods=['get'])
    def timezones(self, request):
        """
        Lista las zonas horarias disponibles
        
        GET /api/notifications/preferences/timezones/
        """
        # Zonas horarias comunes de América Latina
        common_timezones = [
            'America/Bogota',
            'America/Mexico_City',
            'America/Lima',
            'America/Buenos_Aires',
            'America/Santiago',
            'America/Caracas',
            'America/La_Paz',
            'America/Montevideo',
            'America/Asuncion',
            'America/Guayaquil',
            'America/Panama',
            'America/Costa_Rica',
            'America/Guatemala',
            'America/Managua',
            'America/Tegucigalpa',
            'America/El_Salvador',
            'America/Santo_Domingo',
            'America/Havana',
            'America/New_York',
            'America/Chicago',
            'America/Denver',
            'America/Los_Angeles',
            'Europe/Madrid',
            'Europe/London',
            'UTC',
        ]
        
        timezones_data = []
        for tz_name in common_timezones:
            try:
                pytz.timezone(tz_name)
                timezones_data.append({
                    'timezone': tz_name,
                    'display_name': tz_name.replace('_', ' ')
                })
            except Exception:
                pass
        
        serializer = TimezoneListSerializer(timezones_data, many=True)
        return Response(serializer.data)
