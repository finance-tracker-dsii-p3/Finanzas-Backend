"""
Tests para la API de Presupuestos (HU-07)
Tests esenciales para GitHub workflow
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from categories.models import Category
from budgets.models import Budget
from decimal import Decimal
from datetime import date

User = get_user_model()


class BudgetsApiTests(TestCase):
    """Tests esenciales para endpoints de presupuestos"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = Client()
        
        # Crear usuario y token
        self.user = User.objects.create_user(
            identification='ID-TEST-001',
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='user',
            is_verified=True
        )
        self.token = Token.objects.create(user=self.user)
        
        # Crear categoría de gasto
        self.category = Category.objects.create(
            user=self.user,
            name='Comida',
            type='expense',
            color='#DC2626',
            icon='fa-utensils'
        )

    def test_budgets_list_endpoint_exists(self):
        """Verificar que el endpoint de lista existe"""
        response = self.client.get(
            '/api/budgets/',
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        self.assertNotEqual(response.status_code, 404)

    def test_create_budget_requires_authentication(self):
        """Verificar que crear presupuesto requiere autenticación"""
        response = self.client.post('/api/budgets/', {
            'category': self.category.id,
            'amount': 400000,
            'calculation_mode': 'base',
            'period': 'monthly'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_create_budget_success(self):
        """Verificar que se puede crear un presupuesto"""
        response = self.client.post(
            '/api/budgets/',
            {
                'category': self.category.id,
                'amount': 400000,
                'calculation_mode': 'base',
                'period': 'monthly'
            },
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Budget.objects.count(), 1)
        
        budget = Budget.objects.first()
        self.assertEqual(budget.user, self.user)
        self.assertEqual(budget.category, self.category)
        self.assertEqual(budget.amount, Decimal('400000.00'))

    def test_cannot_create_duplicate_budget(self):
        """Verificar que no se pueden crear presupuestos duplicados"""
        # Crear primer presupuesto
        Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('400000.00'),
            calculation_mode='base',
            period='monthly'
        )
        
        # Intentar crear duplicado
        response = self.client.post(
            '/api/budgets/',
            {
                'category': self.category.id,
                'amount': 500000,
                'calculation_mode': 'base',
                'period': 'monthly'
            },
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        self.assertEqual(response.status_code, 400)

    def test_budget_stats_endpoint(self):
        """Verificar que el endpoint de estadísticas funciona"""
        # Crear un presupuesto
        Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('400000.00'),
            calculation_mode='base',
            period='monthly'
        )
        
        response = self.client.get(
            '/api/budgets/stats/',
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_budgets', response.json())

    def test_monthly_summary_endpoint(self):
        """Verificar que el endpoint de resumen mensual funciona"""
        response = self.client.get(
            '/api/budgets/monthly_summary/',
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        self.assertEqual(response.status_code, 200)

    def test_categories_without_budget_endpoint(self):
        """Verificar que el endpoint de categorías sin presupuesto funciona"""
        response = self.client.get(
            '/api/budgets/categories_without_budget/',
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('categories', data)
        # Debe incluir nuestra categoría sin presupuesto
        self.assertEqual(len(data['categories']), 1)

    def test_budget_model_calculation_methods(self):
        """Verificar que los métodos de cálculo del modelo funcionan"""
        budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('400000.00'),
            calculation_mode='base',
            period='monthly'
        )
        
        # Verificar métodos básicos
        self.assertEqual(budget.get_spent_amount(), Decimal('0.00'))
        self.assertEqual(budget.get_spent_percentage(), Decimal('0.00'))
        self.assertEqual(budget.get_remaining_amount(), Decimal('400000.00'))
        self.assertFalse(budget.is_over_budget())
        self.assertFalse(budget.is_alert_triggered())
        self.assertEqual(budget.get_status(), 'good')

    def test_budget_period_dates(self):
        """Verificar que get_period_dates funciona correctamente"""
        budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('400000.00'),
            calculation_mode='base',
            period='monthly',
            start_date=date(2025, 11, 1)
        )
        
        start_date, end_date = budget.get_period_dates()
        self.assertEqual(start_date.month, 11)
        self.assertEqual(end_date.month, 11)
        self.assertEqual(start_date.day, 1)
        # Noviembre tiene 30 días
        self.assertEqual(end_date.day, 30)

    def test_toggle_active_endpoint(self):
        """Verificar que se puede activar/desactivar presupuesto"""
        budget = Budget.objects.create(
            user=self.user,
            category=self.category,
            amount=Decimal('400000.00'),
            calculation_mode='base',
            period='monthly',
            is_active=True
        )
        
        response = self.client.post(
            f'/api/budgets/{budget.id}/toggle_active/',
            HTTP_AUTHORIZATION=f'Token {self.token.key}'
        )
        self.assertEqual(response.status_code, 200)
        
        budget.refresh_from_db()
        self.assertFalse(budget.is_active)
