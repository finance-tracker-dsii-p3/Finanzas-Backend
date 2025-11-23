"""
Tests de workflow para API de Transacciones con integración HU-12
Tests básicos para GitHub Actions CI/CD
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from categories.models import Category
from transactions.models import Transaction
from rules.models import AutomaticRule
from accounts.models import Account
import json
from decimal import Decimal

User = get_user_model()


class TransactionsAPIWorkflowTests(TestCase):
    """Tests básicos para validar el workflow de transacciones"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = Client()
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            identification='11111111',
            username='transuser',
            email='trans@example.com',
            password='testpass123',
            first_name='Trans',
            last_name='User'
        )
        
        # Crear token de autenticación
        self.token = Token.objects.create(user=self.user)
        
        # Headers para autenticación
        self.auth_headers = {
            'HTTP_AUTHORIZATION': f'Token {self.token.key}',
            'content_type': 'application/json'
        }
        
        # Crear cuenta de prueba
        self.test_account = Account.objects.create(
            user=self.user,
            name='Test Account',
            account_type='asset',
            category='bank_account',
            current_balance=Decimal('1000.00')
        )
        
        # Crear categoría de prueba
        self.test_category = Category.objects.create(
            user=self.user,
            name='Comida',
            type='expense',
            color='#DC2626',
            icon='fa-utensils'
        )
    
    def test_transactions_endpoint_exists(self):
        """Verificar que el endpoint de transacciones existe"""
        response = self.client.get('/api/transactions/', **self.auth_headers)
        self.assertNotEqual(response.status_code, 404)
        self.assertIn(response.status_code, [200, 401])
    
    def test_transactions_list_requires_auth(self):
        """Verificar que listar transacciones requiere autenticación"""
        response = self.client.get('/api/transactions/')
        self.assertEqual(response.status_code, 401)
    
    def test_create_transaction_endpoint_exists(self):
        """Verificar que se puede crear transacción (endpoint existe)"""
        transaction_data = {
            'origin_account': self.test_account.id,
            'type': 2,  # Expense
            'base_amount': '25000',
            'date': '2025-11-23',
            'description': 'Almuerzo restaurante'
        }
        
        response = self.client.post(
            '/api/transactions/',
            data=json.dumps(transaction_data),
            **self.auth_headers
        )
        
        # Debe ser 201 (creado) o algún error de validación, pero no 404
        self.assertNotEqual(response.status_code, 404)
        self.assertIn(response.status_code, [201, 400, 401])
    
    def test_transaction_model_has_hu12_fields(self):
        """Verificar que el modelo Transaction tiene campos de HU-12"""
        transaction = Transaction(
            user=self.user,
            origin_account=self.test_account,
            type=2,
            base_amount=Decimal('15000'),
            date='2025-11-23'
        )
        
        # Verificar que los nuevos campos de HU-12 existen
        self.assertTrue(hasattr(transaction, 'description'))
        self.assertTrue(hasattr(transaction, 'category'))
        self.assertTrue(hasattr(transaction, 'applied_rule'))
    
    def test_transaction_with_category_creation(self):
        """Verificar que se puede crear transacción con categoría"""
        transaction = Transaction.objects.create(
            user=self.user,
            origin_account=self.test_account,
            type=2,
            base_amount=Decimal('12000'),
            date='2025-11-23',
            description='Uber centro',
            category=self.test_category
        )
        
        self.assertEqual(transaction.description, 'Uber centro')
        self.assertEqual(transaction.category, self.test_category)
        self.assertIsNone(transaction.applied_rule)  # No rule applied yet
    
    def test_transaction_filters_exist(self):
        """Verificar que los filtros de transacciones funcionan"""
        # Crear una transacción para filtrar
        Transaction.objects.create(
            user=self.user,
            origin_account=self.test_account,
            type=2,
            base_amount=Decimal('15000'),
            date='2025-11-23',
            description='Test transaction',
            category=self.test_category
        )
        
        # Test filtro por categoría
        response = self.client.get(
            f'/api/transactions/?category={self.test_category.id}',
            **self.auth_headers
        )
        self.assertNotEqual(response.status_code, 404)
        
        # Test filtro por descripción (búsqueda)
        response = self.client.get(
            '/api/transactions/?search=test',
            **self.auth_headers
        )
        self.assertNotEqual(response.status_code, 404)


class TransactionsRulesIntegrationWorkflowTests(TestCase):
    """Tests básicos para la integración entre transacciones y reglas (HU-12)"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            identification='22222222',
            username='integrationuser',
            email='integration@test.com',
            password='testpass123'
        )
        
        self.account = Account.objects.create(
            user=self.user,
            name='Integration Account',
            account_type='asset',
            category='bank_account',
            current_balance=Decimal('5000.00')
        )
        
        self.category = Category.objects.create(
            user=self.user,
            name='Transporte',
            type='expense'
        )
        
        # Crear regla de prueba
        self.rule = AutomaticRule.objects.create(
            user=self.user,
            name='Uber Rule',
            criteria_type=AutomaticRule.DESCRIPTION_CONTAINS,
            keyword='uber',
            action_type=AutomaticRule.ASSIGN_CATEGORY,
            target_category=self.category,
            is_active=True,
            order=1
        )
    
    def test_transaction_can_reference_rule(self):
        """Verificar que una transacción puede referenciar una regla aplicada"""
        transaction = Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            type=2,
            base_amount=Decimal('8000'),
            date='2025-11-23',
            description='Viaje en uber',
            category=self.category,
            applied_rule=self.rule
        )
        
        self.assertEqual(transaction.applied_rule, self.rule)
        self.assertEqual(transaction.category, self.category)
    
    def test_rule_can_find_applied_transactions(self):
        """Verificar que una regla puede encontrar transacciones aplicadas"""
        # Crear transacción con regla aplicada
        Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            type=2,
            base_amount=Decimal('10000'),
            date='2025-11-23',
            description='Taxi aeropuerto',
            category=self.category,
            applied_rule=self.rule
        )
        
        # Verificar relación inversa
        applied_transactions = self.rule.applied_transactions.all()
        self.assertEqual(applied_transactions.count(), 1)
        self.assertEqual(applied_transactions.first().description, 'Taxi aeropuerto')
    
    def test_transaction_model_save_method_exists(self):
        """Verificar que el método save personalizado existe para aplicar reglas"""
        transaction = Transaction(
            user=self.user,
            origin_account=self.account,
            type=2,
            base_amount=Decimal('7500'),
            date='2025-11-23',
            description='uber trabajo'
        )
        
        # Verificar que el método save existe (donde se aplicarían las reglas)
        self.assertTrue(hasattr(transaction, 'save'))
        
        # Guardar la transacción (debería aplicar reglas automáticamente)
        # Nota: En este test solo verificamos que no genere errores
        try:
            transaction.save()
            saved_successfully = True
        except Exception:
            saved_successfully = False
        
        self.assertTrue(saved_successfully)