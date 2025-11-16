"""
Tests para el modelo Category y sus validaciones
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from categories.models import Category

User = get_user_model()


class CategoryModelTest(TestCase):
    """Tests para el modelo Category"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.user = User.objects.create_user(
            identification='CAT-TEST-001',
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='user'
        )
    
    def test_create_category(self):
        """Probar creación básica de categoría"""
        category = Category.objects.create(
            user=self.user,
            name='Comida',
            type=Category.EXPENSE,
            color='#DC2626',
            icon='fa-utensils'
        )
        
        self.assertEqual(category.name, 'Comida')
        self.assertEqual(category.type, Category.EXPENSE)
        self.assertTrue(category.is_active)
        self.assertEqual(str(category), 'Comida (Gasto)')
    
    def test_category_name_title_case(self):
        """Probar que el nombre se convierte a title case"""
        category = Category.objects.create(
            user=self.user,
            name='comida rápida',
            type=Category.EXPENSE,
            color='#DC2626'
        )
        
        self.assertEqual(category.name, 'Comida Rápida')
    
    def test_duplicate_category_validation(self):
        """Probar validación de categorías duplicadas"""
        Category.objects.create(
            user=self.user,
            name='Comida',
            type=Category.EXPENSE,
            color='#DC2626'
        )
        
        # Intentar crear categoría duplicada
        with self.assertRaises(ValidationError):
            duplicate = Category(
                user=self.user,
                name='comida',  # Mismo nombre, diferente case
                type=Category.EXPENSE,
                color='#059669'
            )
            duplicate.full_clean()
    
    def test_same_name_different_type_allowed(self):
        """Probar que se permite mismo nombre en diferentes tipos"""
        Category.objects.create(
            user=self.user,
            name='Regalos',
            type=Category.INCOME,
            color='#059669'
        )
        
        # Debe permitir crear con mismo nombre pero tipo diferente
        category2 = Category.objects.create(
            user=self.user,
            name='Regalos',
            type=Category.EXPENSE,
            color='#DC2626'
        )
        
        self.assertEqual(category2.name, 'Regalos')
        self.assertEqual(category2.type, Category.EXPENSE)
    
    def test_same_name_different_user_allowed(self):
        """Probar que diferentes usuarios pueden tener categorías con mismo nombre"""
        user2 = User.objects.create_user(
            identification='CAT-TEST-002',
            username='testuser2',
            email='test2@example.com',
            password='testpass123',
            role='user'
        )
        
        Category.objects.create(
            user=self.user,
            name='Comida',
            type=Category.EXPENSE,
            color='#DC2626'
        )
        
        # Debe permitir a otro usuario crear categoría con mismo nombre
        category2 = Category.objects.create(
            user=user2,
            name='Comida',
            type=Category.EXPENSE,
            color='#059669'
        )
        
        self.assertEqual(category2.user, user2)
    
    def test_invalid_color_format(self):
        """Probar validación de formato de color"""
        with self.assertRaises(ValidationError):
            category = Category(
                user=self.user,
                name='Test',
                type=Category.EXPENSE,
                color='#FFF'  # Formato inválido (debe ser #RRGGBB)
            )
            category.full_clean()
    
    def test_color_contrast_validation(self):
        """Probar validación de contraste de color"""
        # Color muy claro (poco contraste con blanco)
        with self.assertRaises(ValidationError):
            category = Category(
                user=self.user,
                name='Test',
                type=Category.EXPENSE,
                color='#FFFFFF'  # Blanco puro, sin contraste
            )
            category.full_clean()
    
    def test_can_be_deleted(self):
        """Probar método can_be_deleted"""
        category = Category.objects.create(
            user=self.user,
            name='Comida',
            type=Category.EXPENSE,
            color='#DC2626'
        )
        
        # Sin transacciones ni presupuestos, debe poder eliminarse
        self.assertTrue(category.can_be_deleted())
    
    def test_get_usage_count(self):
        """Probar método get_usage_count"""
        category = Category.objects.create(
            user=self.user,
            name='Comida',
            type=Category.EXPENSE,
            color='#DC2626'
        )
        
        # Sin transacciones, debe retornar 0
        self.assertEqual(category.get_usage_count(), 0)
    
    def test_ordering(self):
        """Probar ordenamiento de categorías"""
        cat1 = Category.objects.create(
            user=self.user,
            name='Z Último',
            type=Category.EXPENSE,
            color='#DC2626',
            order=3
        )
        
        cat2 = Category.objects.create(
            user=self.user,
            name='A Primero',
            type=Category.EXPENSE,
            color='#059669',
            order=1
        )
        
        cat3 = Category.objects.create(
            user=self.user,
            name='M Medio',
            type=Category.EXPENSE,
            color='#2563EB',
            order=2
        )
        
        categories = Category.objects.filter(user=self.user)
        
        # Debe ordenar por order primero, luego por name
        self.assertEqual(categories[0], cat2)
        self.assertEqual(categories[1], cat3)
        self.assertEqual(categories[2], cat1)
