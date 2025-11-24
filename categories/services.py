"""
Services para lógica de negocio de categorías
"""
from django.db import transaction
from .models import Category
import logging

logger = logging.getLogger(__name__)


class CategoryService:
    """
    Service class para operaciones de negocio relacionadas con categorías
    """
    
    @staticmethod
    def get_user_categories(user, include_inactive=False, category_type=None):
        """
        Obtener todas las categorías de un usuario
        
        Args:
            user: Usuario propietario
            include_inactive (bool): Si incluir categorías inactivas
            category_type (str): Filtrar por tipo (income/expense)
            
        Returns:
            QuerySet de categorías del usuario
        """
        queryset = Category.objects.filter(user=user).order_by('order', 'name')
        
        if not include_inactive:
            queryset = queryset.filter(is_active=True)
        
        if category_type:
            queryset = queryset.filter(type=category_type)
            
        return queryset
    
    @staticmethod
    def get_categories_stats(user):
        """
        Calcular estadísticas sobre las categorías del usuario
        
        Args:
            user: Usuario propietario
            
        Returns:
            dict: Estadísticas completas
        """
        categories = Category.objects.filter(user=user)
        
        active_count = categories.filter(is_active=True).count()
        inactive_count = categories.filter(is_active=False).count()
        income_count = categories.filter(type=Category.INCOME).count()
        expense_count = categories.filter(type=Category.EXPENSE).count()
        
        # Ordenar por uso (cuando se implementen transacciones)
        # Por ahora, ordenar por nombre
        most_used = list(
            categories.filter(is_active=True)
            .order_by('name')[:5]
            .values('id', 'name', 'type', 'color', 'icon')
        )
        
        least_used = list(
            categories.filter(is_active=True)
            .order_by('-name')[:5]
            .values('id', 'name', 'type', 'color', 'icon')
        )
        
        return {
            'total_categories': categories.count(),
            'active_categories': active_count,
            'inactive_categories': inactive_count,
            'income_categories': income_count,
            'expense_categories': expense_count,
            'most_used': most_used,
            'least_used': least_used
        }
    
    @staticmethod
    @transaction.atomic
    def create_category(user, category_data):
        """
        Crear nueva categoría con validaciones de negocio
        
        Args:
            user: Usuario propietario
            category_data (dict): Datos de la categoría
            
        Returns:
            Category: Categoría creada
        """
        # Validar límite de categorías por usuario
        user_categories_count = Category.objects.filter(user=user).count()
        
        if user_categories_count >= 100:
            raise ValueError('Has alcanzado el límite máximo de categorías (100)')
        
        # Crear la categoría
        category_data['user'] = user
        category = Category.objects.create(**category_data)
        
        logger.info(f'Usuario {user.id} creó categoría: {category.name} ({category.type})')
        
        return category
    
    @staticmethod
    @transaction.atomic
    def update_category(category, update_data):
        """
        Actualizar categoría existente
        
        Args:
            category (Category): Categoría a actualizar
            update_data (dict): Datos a actualizar
            
        Returns:
            Category: Categoría actualizada
        """
        # No permitir editar categorías del sistema
        if category.is_default:
            raise ValueError('No puedes editar categorías del sistema')
        
        # Actualizar campos
        for field, value in update_data.items():
            setattr(category, field, value)
        
        category.full_clean()
        category.save()
        
        logger.info(f'Categoría {category.id} actualizada: {category.name}')
        
        return category
    
    @staticmethod
    @transaction.atomic
    def delete_category(category, target_category_id=None):
        """
        Eliminar categoría con reasignación opcional
        
        Args:
            category (Category): Categoría a eliminar
            target_category_id (int): ID de categoría destino para reasignar
            
        Returns:
            dict: Resultado de la operación
            
        Raises:
            ValueError: Si no se puede eliminar la categoría
        """
        # No permitir eliminar categorías del sistema
        if category.is_default:
            raise ValueError('No puedes eliminar categorías del sistema')
        
        # Verificar si tiene datos relacionados
        related_data = category.get_related_data()
        has_related_data = (
            related_data['transactions_count'] > 0 or 
            related_data['budgets_count'] > 0
        )
        
        if has_related_data and not target_category_id:
            raise ValueError(
                'Esta categoría tiene transacciones o presupuestos asociados. '
                'Debes proporcionar una categoría destino para reasignar.'
            )
        
        result = {
            'reassigned_transactions': 0,
            'reassigned_budgets': 0,
            'category_name': category.name
        }
        
        # Reasignar si es necesario
        if has_related_data and target_category_id:
            try:
                target_category = Category.objects.get(
                    pk=target_category_id,
                    user=category.user,
                    type=category.type
                )
            except Category.DoesNotExist:
                raise ValueError(
                    'La categoría destino no existe o no es válida para reasignación.'
                )
            
            # TODO: Reasignar transacciones cuando se implemente el modelo
            # transactions_updated = category.transactions.update(category=target_category)
            # result['reassigned_transactions'] = transactions_updated
            
            # Reasignar presupuestos
            budgets_updated = category.budgets.update(category=target_category)
            result['reassigned_budgets'] = budgets_updated
            
            logger.info(
                f'Reasignadas transacciones y presupuestos de categoría {category.id} '
                f'a categoría {target_category.id}'
            )
        
        # Eliminar la categoría
        category_id = category.id
        category_name = category.name
        category.delete()
        
        logger.info(f'Categoría {category_id} ({category_name}) eliminada')
        
        return result
    
    @staticmethod
    @transaction.atomic
    def toggle_active(category):
        """
        Activar o desactivar una categoría
        
        Args:
            category (Category): Categoría a cambiar estado
            
        Returns:
            Category: Categoría actualizada
        """
        # No permitir desactivar categorías del sistema
        if category.is_default and category.is_active:
            raise ValueError('No puedes desactivar categorías del sistema')
        
        category.is_active = not category.is_active
        category.save(update_fields=['is_active', 'updated_at'])
        
        action = 'activada' if category.is_active else 'desactivada'
        logger.info(f'Categoría {category.id} ({category.name}) {action}')
        
        return category
    
    @staticmethod
    @transaction.atomic
    def bulk_update_order(user, order_data):
        """
        Actualizar el orden de múltiples categorías
        
        Args:
            user: Usuario propietario
            order_data (list): Lista de dicts con {id: order}
            
        Returns:
            int: Número de categorías actualizadas
        """
        updated_count = 0
        
        for item in order_data:
            category_id = item['id']
            new_order = item['order']
            
            try:
                category = Category.objects.get(pk=category_id, user=user)
                category.order = new_order
                category.save(update_fields=['order', 'updated_at'])
                updated_count += 1
            except Category.DoesNotExist:
                logger.warning(
                    f'Categoría {category_id} no encontrada para usuario {user.id}'
                )
                continue
        
        logger.info(f'Actualizado orden de {updated_count} categorías para usuario {user.id}')
        
        return updated_count
    
    @staticmethod
    def validate_category_deletion(category):
        """
        Validar si una categoría puede ser eliminada y obtener información
        
        Args:
            category (Category): Categoría a validar
            
        Returns:
            dict: Información sobre la validación
        """
        result = {
            'can_delete': True,
            'requires_reassignment': False,
            'warnings': [],
            'errors': [],
            'related_data': category.get_related_data()
        }
        
        # Verificar si es categoría del sistema
        if category.is_default:
            result['can_delete'] = False
            result['errors'].append('No puedes eliminar categorías del sistema')
            return result
        
        # Verificar datos relacionados
        related_data = result['related_data']
        has_transactions = related_data['transactions_count'] > 0
        has_budgets = related_data['budgets_count'] > 0
        
        if has_transactions or has_budgets:
            result['requires_reassignment'] = True
            result['warnings'].append(
                f'Esta categoría tiene {related_data["transactions_count"]} transacciones '
                f'y {related_data["budgets_count"]} presupuestos asociados. '
                f'Deberás reasignarlos a otra categoría.'
            )
        
        return result
    
    @staticmethod
    def create_default_categories(user):
        """
        Crear categorías por defecto para un nuevo usuario
        
        Args:
            user: Usuario para el que crear las categorías
            
        Returns:
            list: Lista de categorías creadas
        """
        default_income_categories = [
            {'name': 'Salario', 'icon': 'fa-money-bill-wave', 'color': '#059669', 'order': 1},  # Verde más oscuro
            {'name': 'Freelance', 'icon': 'fa-briefcase', 'color': '#2563EB', 'order': 2},  # Azul más oscuro
            {'name': 'Inversiones', 'icon': 'fa-chart-line', 'color': '#7C3AED', 'order': 3},  # Morado más oscuro
            {'name': 'Regalos', 'icon': 'fa-gift', 'color': '#DB2777', 'order': 4},  # Rosa más oscuro
            {'name': 'Otros Ingresos', 'icon': 'fa-hand-holding-usd', 'color': '#0D9488', 'order': 5},  # Turquesa más oscuro
        ]
        
        default_expense_categories = [
            {'name': 'Comida', 'icon': 'fa-utensils', 'color': '#DC2626', 'order': 1},  # Rojo más oscuro
            {'name': 'Transporte', 'icon': 'fa-car', 'color': '#EA580C', 'order': 2},  # Naranja más oscuro
            {'name': 'Vivienda', 'icon': 'fa-home', 'color': '#4F46E5', 'order': 3},  # Índigo más oscuro
            {'name': 'Servicios', 'icon': 'fa-bolt', 'color': '#7C3AED', 'order': 4},  # Morado más oscuro
            {'name': 'Entretenimiento', 'icon': 'fa-film', 'color': '#C026D3', 'order': 5},  # Fucsia
            {'name': 'Salud', 'icon': 'fa-heart', 'color': '#DC2626', 'order': 6},  # Rojo oscuro
            {'name': 'Educación', 'icon': 'fa-graduation-cap', 'color': '#1D4ED8', 'order': 7},  # Azul oscuro
            {'name': 'Ropa', 'icon': 'fa-tshirt', 'color': '#047857', 'order': 8},  # Verde muy oscuro
            {'name': 'Compras', 'icon': 'fa-shopping-cart', 'color': '#C2410C', 'order': 9},  # Naranja muy oscuro
            {'name': 'Otros Gastos', 'icon': 'fa-question-circle', 'color': '#4B5563', 'order': 10},  # Gris oscuro
        ]
        
        created_categories = []
        
        # Crear categorías de ingresos
        for cat_data in default_income_categories:
            try:
                category = Category.objects.create(
                    user=user,
                    type=Category.INCOME,
                    is_default=False,  # Ahora son editables por el usuario
                    **cat_data
                )
                created_categories.append(category)
            except Exception as e:
                logger.warning(f'Error creando categoría por defecto {cat_data["name"]}: {e}')
        
        # Crear categorías de gastos
        for cat_data in default_expense_categories:
            try:
                category = Category.objects.create(
                    user=user,
                    type=Category.EXPENSE,
                    is_default=False,
                    **cat_data
                )
                created_categories.append(category)
            except Exception as e:
                logger.warning(f'Error creando categoría por defecto {cat_data["name"]}: {e}')
        
        logger.info(
            f'Creadas {len(created_categories)} categorías por defecto para usuario {user.id}'
        )
        
        return created_categories
