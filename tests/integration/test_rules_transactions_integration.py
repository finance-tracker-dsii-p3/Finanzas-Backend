"""
Tests de integración completa entre Rules y Transactions (HU-12)
Tests para validar que el motor de reglas funciona correctamente
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from categories.models import Category
from transactions.models import Transaction
from rules.models import AutomaticRule
from accounts.models import Account
from rules.services import RuleEngineService
from decimal import Decimal

User = get_user_model()


class RulesTransactionsIntegrationTests(TestCase):
    """Tests de integración completa para HU-12"""
    
    def setUp(self):
        """Configuración completa para tests de integración"""
        # Usuario de prueba
        self.user = User.objects.create_user(
            email='integration@test.com',
            password='testpass123'
        )
        
        # Cuenta de prueba
        self.account = Account.objects.create(
            user=self.user,
            name='Test Integration Account',
            type='checking',
            balance=Decimal('10000.00')
        )
        
        # Categorías de prueba
        self.transport_category = Category.objects.create(
            user=self.user,
            name='Transporte',
            type='expense',
            color='#EA580C'
        )
        
        self.food_category = Category.objects.create(
            user=self.user,
            name='Comida',
            type='expense',
            color='#DC2626'
        )
        
        # Reglas de prueba
        self.uber_rule = AutomaticRule.objects.create(
            user=self.user,
            name='Regla Uber',
            criteria_type=AutomaticRule.DESCRIPTION_CONTAINS,
            keyword='uber',
            action_type=AutomaticRule.ASSIGN_CATEGORY,
            target_category=self.transport_category,
            is_active=True,
            order=1
        )
        
        self.restaurant_rule = AutomaticRule.objects.create(
            user=self.user,
            name='Regla Restaurante',
            criteria_type=AutomaticRule.DESCRIPTION_CONTAINS,
            keyword='restaurante',
            action_type=AutomaticRule.ASSIGN_CATEGORY,
            target_category=self.food_category,
            is_active=True,
            order=2
        )
    
    def test_rule_engine_service_exists(self):
        """Verificar que el servicio del motor de reglas existe"""
        self.assertTrue(hasattr(RuleEngineService, 'apply_rules_to_transaction'))
        self.assertTrue(hasattr(RuleEngineService, 'preview_rule_application'))
    
    def test_transaction_matches_rule_correctly(self):
        """Verificar que las transacciones coinciden con reglas correctamente"""
        # Crear transacción que debe coincidir con regla Uber
        transaction = Transaction(
            user=self.user,
            origin_account=self.account,
            type=2,
            base_amount=Decimal('12000'),
            date='2025-11-23',
            description='Pago Uber centro'
        )
        
        # Verificar que la regla coincide
        matches = self.uber_rule.matches_transaction(transaction)
        self.assertTrue(matches)
        
        # Verificar que la otra regla NO coincide
        no_matches = self.restaurant_rule.matches_transaction(transaction)
        self.assertFalse(no_matches)
    
    def test_rule_application_priority(self):
        """Verificar que las reglas se aplican por prioridad correcta"""
        # Crear regla con prioridad más alta (menor número)
        high_priority_rule = AutomaticRule.objects.create(
            user=self.user,
            name='Alta Prioridad',
            criteria_type=AutomaticRule.DESCRIPTION_CONTAINS,
            keyword='uber',  # Mismo keyword que uber_rule
            action_type=AutomaticRule.ASSIGN_TAG,
            target_tag='priority_tag',
            is_active=True,
            order=0  # Prioridad más alta
        )
        
        transaction_data = {
            'description': 'uber viaje',
            'user': self.user
        }
        
        # Obtener reglas que coinciden
        matching_rules = RuleEngineService.get_matching_rules(
            user=self.user,
            description='uber viaje'
        )
        
        # La primera regla debe ser la de mayor prioridad
        self.assertTrue(len(matching_rules) >= 1)
        self.assertEqual(matching_rules[0], high_priority_rule)
    
    def test_inactive_rules_dont_apply(self):
        """Verificar que las reglas inactivas no se aplican"""
        # Desactivar regla
        self.uber_rule.is_active = False
        self.uber_rule.save()
        
        # Buscar reglas que coincidan
        matching_rules = RuleEngineService.get_matching_rules(
            user=self.user,
            description='uber centro'
        )
        
        # No debe incluir la regla inactiva
        self.assertNotIn(self.uber_rule, matching_rules)
    
    def test_rule_statistics_calculation(self):
        """Verificar que las estadísticas de reglas se calculan correctamente"""
        # Crear transacciones con regla aplicada
        for i in range(3):
            Transaction.objects.create(
                user=self.user,
                origin_account=self.account,
                type=2,
                base_amount=Decimal(f'{10000 + i * 1000}'),
                date='2025-11-23',
                description=f'Uber viaje {i}',
                category=self.transport_category,
                applied_rule=self.uber_rule
            )
        
        # Verificar conteo de aplicaciones
        applied_count = self.uber_rule.applied_transactions.count()
        self.assertEqual(applied_count, 3)
    
    def test_database_constraints_work(self):
        """Verificar que las restricciones de base de datos funcionan"""
        # Crear regla
        rule = AutomaticRule.objects.create(
            user=self.user,
            name='Test Unique Name',
            criteria_type=AutomaticRule.DESCRIPTION_CONTAINS,
            keyword='test',
            action_type=AutomaticRule.ASSIGN_TAG,
            target_tag='test_tag',
            is_active=True,
            order=1
        )
        
        # Intentar crear otra regla con el mismo nombre debe fallar
        with self.assertRaises(Exception):  # IntegrityError o ValidationError
            AutomaticRule.objects.create(
                user=self.user,
                name='Test Unique Name',  # Nombre duplicado
                criteria_type=AutomaticRule.DESCRIPTION_CONTAINS,
                keyword='other',
                action_type=AutomaticRule.ASSIGN_TAG,
                target_tag='other_tag',
                is_active=True,
                order=2
            )
    
    def test_cascade_deletes_work_correctly(self):
        """Verificar que los borrados en cascada funcionan correctamente"""
        # Crear transacción con regla aplicada
        transaction = Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            type=2,
            base_amount=Decimal('8000'),
            date='2025-11-23',
            description='Test transaction',
            category=self.transport_category,
            applied_rule=self.uber_rule
        )
        
        # Verificar que la transacción tiene regla aplicada
        self.assertEqual(transaction.applied_rule, self.uber_rule)
        
        # Eliminar la regla
        rule_id = self.uber_rule.id
        self.uber_rule.delete()
        
        # Verificar que la transacción aún existe pero sin regla aplicada
        transaction.refresh_from_db()
        self.assertIsNone(transaction.applied_rule)