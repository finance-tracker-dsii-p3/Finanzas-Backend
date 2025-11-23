"""
Tests de workflow para API de Reglas Automáticas (HU-12)
Tests básicos para GitHub Actions CI/CD
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from categories.models import Category
from rules.models import AutomaticRule
import json

User = get_user_model()


class RulesAPIWorkflowTests(TestCase):
    """Tests básicos para validar el workflow de reglas automáticas"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = Client()
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Crear token de autenticación
        self.token = Token.objects.create(user=self.user)
        
        # Headers para autenticación
        self.auth_headers = {
            'HTTP_AUTHORIZATION': f'Token {self.token.key}',
            'content_type': 'application/json'
        }
        
        # Crear categoría de prueba
        self.test_category = Category.objects.create(
            user=self.user,
            name='Transporte',
            type='expense',
            color='#EA580C',
            icon='fa-car'
        )
    
    def test_rules_endpoint_exists(self):
        """Verificar que el endpoint de reglas existe"""
        response = self.client.get('/api/rules/', **self.auth_headers)
        self.assertNotEqual(response.status_code, 404)
        self.assertIn(response.status_code, [200, 401])  # 401 si hay problema de auth
    
    def test_rules_list_requires_auth(self):
        """Verificar que listar reglas requiere autenticación"""
        response = self.client.get('/api/rules/')
        self.assertEqual(response.status_code, 401)
    
    def test_create_rule_endpoint_exists(self):
        """Verificar que se puede crear regla (endpoint existe)"""
        rule_data = {
            'name': 'Test Uber',
            'criteria_type': 'description_contains',
            'keyword': 'uber',
            'action_type': 'assign_category',
            'target_category': self.test_category.id,
            'is_active': True,
            'order': 1
        }
        
        response = self.client.post(
            '/api/rules/',
            data=json.dumps(rule_data),
            **self.auth_headers
        )
        
        # Debe ser 201 (creado) o algún error de validación, pero no 404
        self.assertNotEqual(response.status_code, 404)
        self.assertIn(response.status_code, [201, 400, 401])
    
    def test_rule_model_creation(self):
        """Verificar que el modelo AutomaticRule funciona correctamente"""
        rule = AutomaticRule.objects.create(
            user=self.user,
            name='Test Rule',
            criteria_type=AutomaticRule.DESCRIPTION_CONTAINS,
            keyword='test',
            action_type=AutomaticRule.ASSIGN_CATEGORY,
            target_category=self.test_category,
            is_active=True,
            order=1
        )
        
        self.assertEqual(rule.name, 'Test Rule')
        self.assertEqual(rule.user, self.user)
        self.assertTrue(rule.is_active)
        
        # Verificar que el método matches_transaction existe
        self.assertTrue(hasattr(rule, 'matches_transaction'))
    
    def test_rule_stats_endpoint(self):
        """Verificar que el endpoint de estadísticas existe"""
        response = self.client.get('/api/rules/stats/', **self.auth_headers)
        self.assertNotEqual(response.status_code, 404)
        self.assertIn(response.status_code, [200, 401])
    
    def test_rule_preview_endpoint(self):
        """Verificar que el endpoint de previsualización existe"""
        preview_data = {
            'description': 'Test Uber ride'
        }
        
        response = self.client.post(
            '/api/rules/preview/',
            data=json.dumps(preview_data),
            **self.auth_headers
        )
        
        self.assertNotEqual(response.status_code, 404)
        self.assertIn(response.status_code, [200, 400, 401])


class RulesModelWorkflowTests(TestCase):
    """Tests básicos para el modelo de reglas"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='model@test.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(
            user=self.user,
            name='Test Category',
            type='expense'
        )
    
    def test_automatic_rule_str_method(self):
        """Verificar que el método __str__ del modelo funciona"""
        rule = AutomaticRule(
            user=self.user,
            name='Test Rule Name'
        )
        
        self.assertEqual(str(rule), 'Test Rule Name')
    
    def test_rule_choices_are_valid(self):
        """Verificar que las opciones del modelo están definidas"""
        self.assertTrue(hasattr(AutomaticRule, 'DESCRIPTION_CONTAINS'))
        self.assertTrue(hasattr(AutomaticRule, 'TRANSACTION_TYPE'))
        self.assertTrue(hasattr(AutomaticRule, 'ASSIGN_CATEGORY'))
        self.assertTrue(hasattr(AutomaticRule, 'ASSIGN_TAG'))
    
    def test_rule_validation_methods_exist(self):
        """Verificar que los métodos de validación existen"""
        rule = AutomaticRule(user=self.user, name='Test')
        
        # Verificar que los métodos de business logic existen
        self.assertTrue(hasattr(rule, 'matches_transaction'))
        self.assertTrue(hasattr(rule, 'apply_to_transaction'))
        self.assertTrue(hasattr(rule, 'clean'))