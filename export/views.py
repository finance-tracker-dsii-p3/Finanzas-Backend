from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, date
from .models import ExportJob
from .serializers import ExportJobSerializer
from users.models import User


class ExportJobListCreateView(generics.ListCreateAPIView):
    """
    Vista para listar y crear trabajos de exportación - versión simplificada
    """
    serializer_class = ExportJobSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar trabajos por usuario"""
        return ExportJob.objects.filter(requested_by=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Asignar el usuario actual como solicitante"""
        serializer.save(requested_by=self.request.user)


class ExportJobDetailView(generics.RetrieveAPIView):
    """
    Vista para obtener detalles de un trabajo de exportación
    """
    serializer_class = ExportJobSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar trabajos por usuario"""
        return ExportJob.objects.filter(requested_by=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_export(request, export_id):
    """
    Vista para descargar archivo de exportación
    """
    try:
        export_job = get_object_or_404(
            ExportJob, 
            id=export_id, 
            requested_by=request.user,
            status=ExportJob.COMPLETED
        )
        
        if not export_job.file or not export_job.file.storage.exists(export_job.file.name):
            return Response(
                {"error": "Archivo no encontrado"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        response = HttpResponse(export_job.file.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{export_job.file.name.split("/")[-1]}"'
        return response
        
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_users_data(request):
    """
    Vista básica para obtener datos de usuarios para exportación
    """
    try:
        # Filtros básicos
        search = request.GET.get('search', '')
        role = request.GET.get('role', '')
        is_verified = request.GET.get('is_verified', '')
        
        # Construir queryset
        queryset = User.objects.all()
        
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) | 
                Q(first_name__icontains=search) | 
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        if role:
            queryset = queryset.filter(role=role)
            
        if is_verified:
            queryset = queryset.filter(is_verified=is_verified.lower() == 'true')
        
        # Preparar datos para respuesta
        users_data = []
        for user in queryset.order_by('username'):
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'is_verified': user.is_verified,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat() if user.date_joined else None,
                'last_login': user.last_login.isoformat() if user.last_login else None
            })
        
        return Response({
            'users': users_data,
            'total': len(users_data),
            'exported_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_basic_export(request):
    """
    Vista para crear exportación básica
    """
    try:
        export_type = request.data.get('export_type', 'general_data')
        title = request.data.get('title', f'Exportación {timezone.now().strftime("%Y-%m-%d %H:%M")}')
        format_type = request.data.get('format', 'excel')
        
        # Crear job de exportación
        export_job = ExportJob.objects.create(
            title=title,
            export_type=export_type,
            format=format_type,
            requested_by=request.user
        )
        
        # Aquí se podría procesar la exportación en background
        # Por ahora solo marcamos como completado
        export_job.mark_as_completed()
        
        serializer = ExportJobSerializer(export_job)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {"error": str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )