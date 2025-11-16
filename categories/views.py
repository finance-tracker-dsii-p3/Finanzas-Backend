"""
Views para gestión de categorías de ingresos y gastos
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
import logging

from .models import Category
from .serializers import (
    CategoryListSerializer,
    CategoryDetailSerializer,
    CategoryCreateSerializer,
    CategoryUpdateSerializer,
    CategoryReassignSerializer,
    CategoryStatsSerializer,
    CategoryBulkOrderSerializer
)
from .services import CategoryService

logger = logging.getLogger(__name__)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para gestión de categorías
    
    Proporciona operaciones CRUD completas más acciones adicionales
    para activar/desactivar, reordenar y obtener estadísticas.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar categorías por usuario autenticado"""
        return Category.objects.filter(user=self.request.user).order_by('order', 'name')
    
    def get_serializer_class(self):
        """Seleccionar serializer según la acción"""
        if self.action == 'list':
            return CategoryListSerializer
        elif self.action == 'retrieve':
            return CategoryDetailSerializer
        elif self.action == 'create':
            return CategoryCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CategoryUpdateSerializer
        elif self.action == 'delete_with_reassignment':
            return CategoryReassignSerializer
        elif self.action == 'stats':
            return CategoryStatsSerializer
        elif self.action == 'bulk_update_order':
            return CategoryBulkOrderSerializer
        else:
            return CategoryDetailSerializer
    
    def list(self, request, *args, **kwargs):
        """
        Listar categorías del usuario con filtros opcionales
        
        Query params:
            active_only (bool): Solo categorías activas (default: true)
            type (str): Filtrar por tipo (income/expense)
        """
        queryset = self.get_queryset()
        
        # Filtro por categorías activas
        active_only = request.query_params.get('active_only', 'true').lower() == 'true'
        if active_only:
            queryset = queryset.filter(is_active=True)
        
        # Filtro por tipo
        category_type = request.query_params.get('type')
        if category_type:
            queryset = queryset.filter(type=category_type)
        
        serializer = self.get_serializer(queryset, many=True)
        
        count = queryset.count()
        logger.info(
            f'Usuario {request.user.id} listó categorías: {count} encontradas'
        )
        
        # Si no hay categorías, devolver mensaje informativo
        if count == 0:
            return Response({
                'count': 0,
                'message': 'No tienes categorías creadas. Usa POST /api/categories/create_defaults/ para crear categorías por defecto.',
                'results': []
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def perform_create(self, serializer):
        """Crear categoría asignando el usuario autenticado"""
        try:
            category = serializer.save()
            
            logger.info(
                f'Usuario {self.request.user.id} creó categoría: {category.name} '
                f'({category.get_type_display()})'
            )
            
        except Exception as e:
            logger.warning(
                f'Error al crear categoría para usuario {self.request.user.id}: {str(e)}'
            )
            raise e
    
    def perform_update(self, serializer):
        """Actualizar categoría"""
        try:
            category = serializer.save()
            
            logger.info(
                f'Usuario {self.request.user.id} actualizó categoría: {category.name}'
            )
            
        except Exception as e:
            logger.warning(
                f'Error al actualizar categoría {self.get_object().id}: {str(e)}'
            )
            raise e
    
    def perform_destroy(self, instance):
        """Eliminar categoría sin reasignación (solo si no tiene datos relacionados)"""
        try:
            # Validar eliminación
            validation = CategoryService.validate_category_deletion(instance)
            
            if not validation['can_delete']:
                raise ValueError('; '.join(validation['errors']))
            
            if validation['requires_reassignment']:
                raise ValueError(
                    'Esta categoría tiene transacciones o presupuestos asociados. '
                    'Usa el endpoint /delete_with_reassignment/ para reasignarlos.'
                )
            
            # Eliminar usando service
            result = CategoryService.delete_category(instance)
            
            logger.info(
                f'Usuario {self.request.user.id} eliminó categoría: {instance.name}'
            )
            
        except ValueError as e:
            logger.warning(
                f'Error al eliminar categoría {instance.id}: {str(e)}'
            )
            raise e
    
    @action(detail=True, methods=['post'])
    def delete_with_reassignment(self, request, pk=None):
        """
        Eliminar categoría reasignando transacciones y presupuestos
        
        Body:
            target_category_id (int): ID de la categoría destino
        
        Returns:
            Response: Resultado de la eliminación con contador de reasignaciones
        """
        category = self.get_object()
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request, 'category': category}
        )
        
        if serializer.is_valid():
            try:
                target_category_id = serializer.validated_data['target_category_id']
                
                result = CategoryService.delete_category(
                    category=category,
                    target_category_id=target_category_id
                )
                
                logger.info(
                    f'Usuario {request.user.id} eliminó categoría {category.name} '
                    f'con reasignación a categoría {target_category_id}'
                )
                
                return Response(result, status=status.HTTP_200_OK)
                
            except ValueError as e:
                logger.warning(
                    f'Error al eliminar categoría {category.id} con reasignación: {str(e)}'
                )
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """
        Activar o desactivar una categoría
        
        Returns:
            Response: Categoría actualizada
        """
        category = self.get_object()
        
        try:
            updated_category = CategoryService.toggle_active(category)
            
            action_text = 'activó' if updated_category.is_active else 'desactivó'
            logger.info(
                f'Usuario {request.user.id} {action_text} categoría: {category.name}'
            )
            
            serializer = CategoryDetailSerializer(updated_category)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.warning(
                f'Error al cambiar estado de categoría {category.id}: {str(e)}'
            )
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def validate_deletion(self, request, pk=None):
        """
        Validar si una categoría puede ser eliminada
        
        Returns:
            Response: Información sobre la validación
        """
        category = self.get_object()
        
        try:
            validation_result = CategoryService.validate_category_deletion(category)
            
            logger.info(
                f'Usuario {request.user.id} validó eliminación de categoría {category.name}: '
                f'can_delete={validation_result["can_delete"]}'
            )
            
            return Response(validation_result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(
                f'Error al validar eliminación de categoría {category.id}: {str(e)}'
            )
            return Response(
                {'error': 'Error interno en validación'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Obtener estadísticas de categorías del usuario
        
        Returns:
            Response: Estadísticas completas
        """
        try:
            stats_data = CategoryService.get_categories_stats(request.user)
            
            logger.info(
                f'Generadas estadísticas de categorías para usuario {request.user.id}'
            )
            
            return Response(stats_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(
                f'Error al generar estadísticas para usuario {request.user.id}: {str(e)}'
            )
            return Response(
                {'error': 'Error interno al generar estadísticas'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def bulk_update_order(self, request):
        """
        Actualizar el orden de múltiples categorías
        
        Body:
            categories (list): Lista de {id: int, order: int}
        
        Returns:
            Response: Número de categorías actualizadas
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            try:
                order_data = serializer.validated_data['categories']
                
                updated_count = CategoryService.bulk_update_order(
                    user=request.user,
                    order_data=order_data
                )
                
                logger.info(
                    f'Usuario {request.user.id} actualizó orden de {updated_count} categorías'
                )
                
                return Response(
                    {
                        'updated_count': updated_count,
                        'message': f'{updated_count} categorías actualizadas'
                    },
                    status=status.HTTP_200_OK
                )
                
            except Exception as e:
                logger.error(
                    f'Error al actualizar orden de categorías para usuario {request.user.id}: {str(e)}'
                )
                return Response(
                    {'error': 'Error interno al actualizar orden'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def income(self, request):
        """
        Obtener solo categorías de ingresos activas
        
        Returns:
            Response: Lista de categorías de ingresos
        """
        categories = CategoryService.get_user_categories(
            user=request.user,
            include_inactive=False,
            category_type=Category.INCOME
        )
        
        serializer = CategoryListSerializer(categories, many=True)
        
        count = categories.count()
        logger.info(
            f'Usuario {request.user.id} listó categorías de ingresos: '
            f'{count} encontradas'
        )
        
        if count == 0:
            return Response({
                'count': 0,
                'message': 'No tienes categorías de ingresos. Crea una con POST /api/categories/',
                'results': []
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def expense(self, request):
        """
        Obtener solo categorías de gastos activas
        
        Returns:
            Response: Lista de categorías de gastos
        """
        categories = CategoryService.get_user_categories(
            user=request.user,
            include_inactive=False,
            category_type=Category.EXPENSE
        )
        
        serializer = CategoryListSerializer(categories, many=True)
        
        count = categories.count()
        logger.info(
            f'Usuario {request.user.id} listó categorías de gastos: '
            f'{count} encontradas'
        )
        
        if count == 0:
            return Response({
                'count': 0,
                'message': 'No tienes categorías de gastos. Crea una con POST /api/categories/',
                'results': []
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def create_defaults(self, request):
        """
        Crear categorías por defecto para el usuario
        Solo funciona si el usuario no tiene categorías
        
        Returns:
            Response: Lista de categorías creadas
        """
        # Verificar que no tenga categorías
        existing_categories = Category.objects.filter(user=request.user).count()
        
        if existing_categories > 0:
            return Response(
                {'error': 'Ya tienes categorías creadas. No se pueden crear las predeterminadas.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            created_categories = CategoryService.create_default_categories(request.user)
            
            serializer = CategoryListSerializer(created_categories, many=True)
            
            logger.info(
                f'Usuario {request.user.id} creó {len(created_categories)} categorías por defecto'
            )
            
            return Response(
                {
                    'message': f'{len(created_categories)} categorías creadas exitosamente',
                    'categories': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(
                f'Error al crear categorías por defecto para usuario {request.user.id}: {str(e)}'
            )
            return Response(
                {'error': 'Error al crear categorías por defecto'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
