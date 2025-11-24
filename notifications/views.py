from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer
from .services import NotificationService


class NotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint para gestionar notificaciones - adaptado para proyecto financiero
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Retorna las notificaciones según el rol del usuario
        """
        if self.request.user.role == 'admin':
            # Los admins ven todas las notificaciones
            return Notification.objects.all().order_by('-created_at')
        else:
            # Los usuarios normales solo ven sus propias notificaciones
            return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """
        Solo admins pueden crear notificaciones
        """
        if request.user.role != 'admin':
            return Response({'error': 'Solo administradores pueden crear notificaciones'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_as_read(self, request, pk=None):
        """
        Marcar una notificación específica como leída
        """
        try:
            notification = self.get_object()
            
            # Verificar que la notificación pertenece al usuario actual
            if notification.user != request.user:
                return Response({'error': 'No tienes permiso para modificar esta notificación'}, 
                              status=status.HTTP_403_FORBIDDEN)
            
            success = NotificationService.mark_as_read(notification.id, request.user)
            
            if success:
                return Response({'message': 'Notificación marcada como leída'})
            else:
                return Response({'error': 'Error al marcar la notificación'}, 
                              status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_all_read(self, request):
        """
        Marcar todas las notificaciones del usuario como leídas
        """
        try:
            notifications = Notification.objects.filter(user=request.user, read=False)
            count = notifications.count()
            notifications.update(read=True)
            
            return Response({'message': f'{count} notificaciones marcadas como leídas'})
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Obtener resumen de notificaciones del usuario
        """
        try:
            summary = NotificationService.get_user_notifications_summary(request.user)
            serializer = self.get_serializer(summary['recent'], many=True)
            
            return Response({
                'total': summary['total'],
                'unread': summary['unread'],
                'recent': serializer.data,
                'by_type': list(summary['by_type'])
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def system_alerts_summary(self, request):
        """
        Obtener resumen estadístico de alertas del sistema - adaptado para proyecto financiero
        Solo para administradores
        """
        if request.user.role != 'admin':
            return Response({'error': 'Solo administradores pueden acceder a este endpoint'}, status=403)
        
        from datetime import datetime, timedelta
        
        # Obtener notificaciones de las últimas 30 días
        last_30_days = datetime.now() - timedelta(days=30)
        
        system_notifications = Notification.objects.filter(
            notification_type='system_alert',
            created_at__gte=last_30_days
        ).order_by('-created_at')
        
        # Crear resumen básico por usuario
        users_summary = {}
        for notification in system_notifications:
            username = notification.user.username
            user_name = notification.user.get_full_name()
            
            if username not in users_summary:
                users_summary[username] = {
                    'username': username,
                    'user_name': user_name,
                    'total_notifications': 0,
                    'last_notification': None
                }
            
            users_summary[username]['total_notifications'] += 1
            
            if not users_summary[username]['last_notification'] or notification.created_at > users_summary[username]['last_notification']:
                users_summary[username]['last_notification'] = notification.created_at
        
        return Response({
            'period': 'Últimos 30 días',
            'total_notifications': system_notifications.count(),
            'unique_users': len(users_summary),
            'users_summary': list(users_summary.values()),
            'recent_notifications': NotificationSerializer(
                system_notifications[:5], many=True
            ).data
        })
    
    @action(detail=False, methods=['get'])
    def notifications_summary(self, request):
        """
        Obtener resumen estadístico de notificaciones - simplificado para proyecto financiero
        Solo para administradores
        """
        if request.user.role != 'admin':
            return Response({'error': 'Solo administradores pueden acceder a este endpoint'}, status=403)
        
        from datetime import datetime, timedelta
        
        # Obtener notificaciones de las últimas 30 días
        last_30_days = datetime.now() - timedelta(days=30)
        
        recent_notifications = Notification.objects.filter(
            created_at__gte=last_30_days
        ).order_by('-created_at')
        
        # Crear resumen básico por usuario
        users_summary = {}
        for notification in recent_notifications:
            username = notification.user.username
            user_name = notification.user.get_full_name()
            
            if username not in users_summary:
                users_summary[username] = {
                    'username': username,
                    'user_name': user_name,
                    'total_notifications': 0,
                    'unread_notifications': 0,
                    'last_notification': None
                }
            
            users_summary[username]['total_notifications'] += 1
            if not notification.read:
                users_summary[username]['unread_notifications'] += 1
            
            if not users_summary[username]['last_notification'] or notification.created_at > users_summary[username]['last_notification']:
                users_summary[username]['last_notification'] = notification.created_at
        
        return Response({
            'period': 'Últimos 30 días',
            'total_notifications': recent_notifications.count(),
            'unique_users': len(users_summary),
            'users_summary': list(users_summary.values()),
            'recent_notifications': NotificationSerializer(
                recent_notifications[:5], many=True
            ).data
        })
    
    @action(detail=False, methods=['post'])
    def send_system_alert(self, request):
        """
        Enviar alerta del sistema a usuarios específicos
        Solo para administradores
        """
        if request.user.role != 'admin':
            return Response({'error': 'Solo administradores pueden enviar alertas del sistema'}, status=403)
        
        try:
            title = request.data.get('title')
            message = request.data.get('message')
            user_ids = request.data.get('user_ids', None)
            
            if not title or not message:
                return Response({'error': 'Título y mensaje son requeridos'}, status=400)
            
            notifications_sent = NotificationService.send_system_notification(
                title=title,
                message=message,
                user_ids=user_ids
            )
            
            return Response({
                'message': f'Alerta enviada a {notifications_sent} usuarios',
                'notifications_sent': notifications_sent
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)