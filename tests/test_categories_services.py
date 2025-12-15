"""
Tests para servicios de categorías (categories/services.py)
Fase 1: Aumentar cobertura de tests
"""

from django.contrib.auth import get_user_model
from django.test import TestCase

from budgets.models import Budget
from categories.models import Category
from categories.services import CategoryService

User = get_user_model()


class CategoriesServicesTests(TestCase):
    """Tests para servicios de categorías"""

    def setUp(self):
        """Configuración inicial para cada test"""
        self.user = User.objects.create_user(
            identification="12345678",
            username="testuser",
            email="test@example.com",
            password="testpass123",
            is_verified=True,
        )

        self.category1 = Category.objects.create(
            user=self.user,
            name="Comida",
            type=Category.EXPENSE,
            color="#DC2626",
            icon="fa-utensils",
            is_active=True,
            order=1,
        )

        self.category2 = Category.objects.create(
            user=self.user,
            name="Salario",
            type=Category.INCOME,
            color="#16A34A",
            icon="fa-dollar-sign",
            is_active=True,
            order=2,
        )

        self.inactive_category = Category.objects.create(
            user=self.user,
            name="Inactiva",
            type=Category.EXPENSE,
            color="#000000",
            icon="fa-question-circle",
            is_active=False,
            order=3,
        )

    def test_get_user_categories_all(self):
        """Test: Obtener todas las categorías del usuario"""
        categories = CategoryService.get_user_categories(self.user, include_inactive=True)
        assert categories.count() == 3

    def test_get_user_categories_active_only(self):
        """Test: Obtener solo categorías activas"""
        categories = CategoryService.get_user_categories(self.user, include_inactive=False)
        assert categories.count() == 2
        assert all(cat.is_active for cat in categories)

    def test_get_user_categories_by_type_income(self):
        """Test: Filtrar categorías por tipo income"""
        categories = CategoryService.get_user_categories(
            self.user, include_inactive=False, category_type=Category.INCOME
        )
        assert categories.count() == 1
        assert categories.first().type == Category.INCOME

    def test_get_user_categories_by_type_expense(self):
        """Test: Filtrar categorías por tipo expense"""
        categories = CategoryService.get_user_categories(
            self.user, include_inactive=False, category_type=Category.EXPENSE
        )
        assert categories.count() == 1
        assert categories.first().type == Category.EXPENSE

    def test_get_categories_stats(self):
        """Test: Obtener estadísticas de categorías"""
        stats = CategoryService.get_categories_stats(self.user)

        assert "total_categories" in stats
        assert "active_categories" in stats
        assert "inactive_categories" in stats
        assert "income_categories" in stats
        assert "expense_categories" in stats
        assert "most_used" in stats
        assert "least_used" in stats

        assert stats["total_categories"] == 3
        assert stats["active_categories"] == 2
        assert stats["inactive_categories"] == 1
        assert stats["income_categories"] == 1
        assert stats["expense_categories"] == 2

    def test_create_category_success(self):
        """Test: Crear categoría exitosamente"""
        category_data = {
            "name": "Nueva Categoría",
            "type": Category.EXPENSE,
            "color": "#FF0000",
            "icon": "fa-tags",
        }

        category = CategoryService.create_category(self.user, category_data)
        assert category.name == "Nueva Categoría"
        assert category.user == self.user
        assert Category.objects.filter(id=category.id).exists()

    def test_create_category_limit_reached(self):
        """Test: Error al crear categoría cuando se alcanza el límite"""
        # Crear 100 categorías para alcanzar el límite
        for i in range(98):  # Ya tenemos 3, necesitamos 97 más para llegar a 100
            Category.objects.create(
                user=self.user,
                name=f"Categoría {i}",
                type=Category.EXPENSE,
                color="#000000",
            )

        category_data = {
            "name": "Categoría 101",
            "type": Category.EXPENSE,
            "color": "#FF0000",
        }

        try:
            CategoryService.create_category(self.user, category_data)
            msg = "Debería haber lanzado ValueError"
            raise AssertionError(msg)
        except ValueError as e:
            assert "límite máximo" in str(e)

    def test_create_category_at_limit(self):
        """Test: Crear categoría cuando está justo en el límite (99 categorías)"""
        # Crear 97 categorías más (ya tenemos 3, total 100)
        for i in range(97):
            Category.objects.create(
                user=self.user,
                name=f"Categoría {i}",
                type=Category.EXPENSE,
                color="#000000",
            )

        # Intentar crear una más debería fallar
        category_data = {
            "name": "Categoría 100",
            "type": Category.EXPENSE,
            "color": "#FF0000",
        }

        try:
            CategoryService.create_category(self.user, category_data)
            msg = "Debería haber lanzado ValueError"
            raise AssertionError(msg)
        except ValueError as e:
            assert "límite máximo" in str(e)

    def test_update_category_success(self):
        """Test: Actualizar categoría exitosamente"""
        update_data = {"name": "Comida Actualizada", "color": "#FF0000"}

        updated = CategoryService.update_category(self.category1, update_data)
        assert updated.name == "Comida Actualizada"
        assert updated.color == "#FF0000"
        self.category1.refresh_from_db()
        assert self.category1.name == "Comida Actualizada"

    def test_update_category_default_raises_error(self):
        """Test: Error al actualizar categoría del sistema"""
        default_category = Category.objects.create(
            user=self.user,
            name="Default",
            type=Category.EXPENSE,
            is_default=True,
        )

        update_data = {"name": "Intentar cambiar"}

        try:
            CategoryService.update_category(default_category, update_data)
            msg = "Debería haber lanzado ValueError"
            raise AssertionError(msg)
        except ValueError as e:
            assert "sistema" in str(e)

    def test_delete_category_success(self):
        """Test: Eliminar categoría sin datos relacionados"""
        category_id = self.category1.id
        result = CategoryService.delete_category(self.category1)

        assert "category_name" in result
        assert not Category.objects.filter(id=category_id).exists()

    def test_delete_category_with_reassignment(self):
        """Test: Eliminar categoría con reasignación de presupuestos"""
        # Crear presupuesto asociado
        budget = Budget.objects.create(
            user=self.user,
            category=self.category1,
            amount=100000.00,
            currency="COP",
            period=Budget.MONTHLY,
        )

        # Crear categoría destino
        target_category = Category.objects.create(
            user=self.user,
            name="Destino",
            type=Category.EXPENSE,
            color="#000000",
        )

        result = CategoryService.delete_category(
            self.category1, target_category_id=target_category.id
        )

        assert result["reassigned_budgets"] == 1
        assert not Category.objects.filter(id=self.category1.id).exists()
        budget.refresh_from_db()
        assert budget.category == target_category

    def test_delete_category_default_raises_error(self):
        """Test: Error al eliminar categoría del sistema"""
        default_category = Category.objects.create(
            user=self.user,
            name="Default",
            type=Category.EXPENSE,
            is_default=True,
        )

        try:
            CategoryService.delete_category(default_category)
            msg = "Debería haber lanzado ValueError"
            raise AssertionError(msg)
        except ValueError as e:
            assert "sistema" in str(e)

    def test_delete_category_with_data_requires_reassignment(self):
        """Test: Error al eliminar categoría con datos sin reasignación"""
        # Crear presupuesto asociado
        Budget.objects.create(
            user=self.user,
            category=self.category1,
            amount=100000.00,
            currency="COP",
            period=Budget.MONTHLY,
        )

        try:
            CategoryService.delete_category(self.category1)
            msg = "Debería haber lanzado ValueError"
            raise AssertionError(msg)
        except ValueError as e:
            assert "reasignar" in str(e) or "asociados" in str(e)

    def test_delete_category_invalid_target_category(self):
        """Test: Error al eliminar categoría con categoría destino inválida"""
        # Crear presupuesto asociado
        Budget.objects.create(
            user=self.user,
            category=self.category1,
            amount=100000.00,
            currency="COP",
            period=Budget.MONTHLY,
        )

        try:
            CategoryService.delete_category(self.category1, target_category_id=99999)
            msg = "Debería haber lanzado ValueError"
            raise AssertionError(msg)
        except ValueError as e:
            assert "destino" in str(e) or "válida" in str(e)

    def test_delete_category_target_different_type(self):
        """Test: Error al reasignar a categoría de tipo diferente"""
        # Crear presupuesto asociado
        Budget.objects.create(
            user=self.user,
            category=self.category1,  # EXPENSE
            amount=100000.00,
            currency="COP",
            period=Budget.MONTHLY,
        )

        # Intentar reasignar a categoría de INCOME (tipo diferente)
        try:
            CategoryService.delete_category(
                self.category1, target_category_id=self.category2.id  # INCOME
            )
            msg = "Debería haber lanzado ValueError"
            raise AssertionError(msg)
        except ValueError as e:
            assert "destino" in str(e) or "válida" in str(e)

    def test_toggle_active_success(self):
        """Test: Activar/desactivar categoría"""
        initial_status = self.category1.is_active
        updated = CategoryService.toggle_active(self.category1)

        assert updated.is_active != initial_status
        self.category1.refresh_from_db()
        assert self.category1.is_active != initial_status

    def test_toggle_active_default_raises_error(self):
        """Test: Error al desactivar categoría del sistema"""
        default_category = Category.objects.create(
            user=self.user,
            name="Default",
            type=Category.EXPENSE,
            is_default=True,
            is_active=True,
        )

        try:
            CategoryService.toggle_active(default_category)
            msg = "Debería haber lanzado ValueError"
            raise AssertionError(msg)
        except ValueError as e:
            assert "sistema" in str(e)

    def test_toggle_active_default_already_inactive(self):
        """Test: Activar categoría del sistema que está inactiva (debe funcionar)"""
        default_category = Category.objects.create(
            user=self.user,
            name="Default",
            type=Category.EXPENSE,
            is_default=True,
            is_active=False,  # Ya está inactiva
        )

        # Debería poder activarla
        updated = CategoryService.toggle_active(default_category)
        assert updated.is_active is True

    def test_bulk_update_order_success(self):
        """Test: Actualizar orden de múltiples categorías"""
        order_data = [
            {"id": self.category1.id, "order": 10},
            {"id": self.category2.id, "order": 20},
        ]

        updated_count = CategoryService.bulk_update_order(self.user, order_data)

        assert updated_count == 2
        self.category1.refresh_from_db()
        self.category2.refresh_from_db()
        assert self.category1.order == 10
        assert self.category2.order == 20

    def test_bulk_update_order_invalid_category(self):
        """Test: Actualizar orden ignorando categorías inválidas"""
        order_data = [
            {"id": self.category1.id, "order": 10},
            {"id": 99999, "order": 20},  # No existe
        ]

        updated_count = CategoryService.bulk_update_order(self.user, order_data)

        assert updated_count == 1
        self.category1.refresh_from_db()
        assert self.category1.order == 10

    def test_validate_category_deletion_success(self):
        """Test: Validar eliminación de categoría sin datos"""
        validation = CategoryService.validate_category_deletion(self.category1)

        assert validation["can_delete"] is True
        assert validation["requires_reassignment"] is False
        assert len(validation["errors"]) == 0

    def test_validate_category_deletion_with_data(self):
        """Test: Validar eliminación de categoría con datos relacionados"""
        # Crear presupuesto asociado
        Budget.objects.create(
            user=self.user,
            category=self.category1,
            amount=100000.00,
            currency="COP",
            period=Budget.MONTHLY,
        )

        validation = CategoryService.validate_category_deletion(self.category1)

        assert validation["can_delete"] is True
        assert validation["requires_reassignment"] is True
        assert len(validation["warnings"]) > 0

    def test_validate_category_deletion_default(self):
        """Test: Validar eliminación de categoría del sistema"""
        default_category = Category.objects.create(
            user=self.user,
            name="Default",
            type=Category.EXPENSE,
            is_default=True,
        )

        validation = CategoryService.validate_category_deletion(default_category)

        assert validation["can_delete"] is False
        assert len(validation["errors"]) > 0

    def test_create_default_categories_success(self):
        """Test: Crear categorías por defecto"""
        new_user = User.objects.create_user(
            identification="87654321",
            username="newuser",
            email="new@example.com",
            password="testpass123",
            is_verified=True,
        )

        created = CategoryService.create_default_categories(new_user)

        assert len(created) > 0
        # Verificar que se crearon categorías de ingresos y gastos
        income_count = Category.objects.filter(user=new_user, type=Category.INCOME).count()
        expense_count = Category.objects.filter(user=new_user, type=Category.EXPENSE).count()
        assert income_count > 0
        assert expense_count > 0

    def test_delete_category_with_transactions_and_budgets(self):
        """Test: Eliminar categoría con transacciones y presupuestos"""
        # Crear presupuesto
        budget = Budget.objects.create(
            user=self.user,
            category=self.category1,
            amount=100000.00,
            currency="COP",
            period=Budget.MONTHLY,
        )

        # Crear categoría destino del mismo tipo
        target_category = Category.objects.create(
            user=self.user,
            name="Destino",
            type=Category.EXPENSE,  # Mismo tipo que category1
            color="#000000",
        )

        result = CategoryService.delete_category(
            self.category1, target_category_id=target_category.id
        )

        assert result["reassigned_budgets"] == 1
        assert "category_name" in result
        budget.refresh_from_db()
        assert budget.category == target_category

    def test_get_categories_stats_empty(self):
        """Test: Estadísticas con usuario sin categorías"""
        new_user = User.objects.create_user(
            identification="99999999",
            username="emptyuser",
            email="empty@example.com",
            password="testpass123",
            is_verified=True,
        )

        stats = CategoryService.get_categories_stats(new_user)

        assert stats["total_categories"] == 0
        assert stats["active_categories"] == 0
        assert stats["inactive_categories"] == 0
        assert stats["income_categories"] == 0
        assert stats["expense_categories"] == 0
        assert len(stats["most_used"]) == 0
        assert len(stats["least_used"]) == 0

    def test_validate_category_deletion_with_transactions(self):
        """Test: Validar eliminación de categoría con transacciones"""
        # Nota: Este test verifica la validación, aunque las transacciones
        # no se reasignen aún (está en TODO)
        validation = CategoryService.validate_category_deletion(self.category1)

        # Debería permitir eliminar pero requerir reasignación si hay datos
        assert "can_delete" in validation
        assert "requires_reassignment" in validation
        assert "related_data" in validation

    def test_create_default_categories_with_existing_categories(self):
        """Test: Crear categorías por defecto cuando ya existen algunas"""
        # Crear una categoría existente
        Category.objects.create(
            user=self.user,
            name="Categoría Existente",
            type=Category.EXPENSE,
            color="#DC2626",
            icon="fa-utensils",
        )

        # Crear categorías por defecto
        created = CategoryService.create_default_categories(self.user)
        # Debe crear las categorías por defecto
        assert len(created) > 0

    def test_bulk_update_order_partial_success(self):
        """Test: Actualizar orden parcialmente (algunas categorías válidas, otras no)"""
        # Crear otra categoría
        category3 = Category.objects.create(
            user=self.user,
            name="Categoría 3",
            type=Category.EXPENSE,
            color="#000000",
        )

        order_data = [
            {"id": self.category1.id, "order": 10},
            {"id": 99999, "order": 20},  # No existe
            {"id": category3.id, "order": 30},
        ]

        updated_count = CategoryService.bulk_update_order(self.user, order_data)

        assert updated_count == 2  # Solo 2 se actualizaron
        self.category1.refresh_from_db()
        category3.refresh_from_db()
        assert self.category1.order == 10
        assert category3.order == 30

    def test_delete_category_no_data_no_reassignment(self):
        """Test: Eliminar categoría sin datos relacionados no requiere reasignación"""
        # Crear categoría sin datos relacionados
        empty_category = Category.objects.create(
            user=self.user,
            name="Categoría Vacía",
            type=Category.EXPENSE,
            color="#000000",
            icon="fa-question-circle",
        )

        result = CategoryService.delete_category(empty_category)
        assert result["reassigned_transactions"] == 0
        assert result["reassigned_budgets"] == 0
        assert not Category.objects.filter(id=empty_category.id).exists()

    def test_validate_category_deletion_no_data(self):
        """Test: Validar eliminación de categoría sin datos relacionados"""
        empty_category = Category.objects.create(
            user=self.user,
            name="Categoría Vacía",
            type=Category.EXPENSE,
            color="#000000",
            icon="fa-question-circle",
        )

        validation = CategoryService.validate_category_deletion(empty_category)
        assert validation["can_delete"] is True
        assert validation["requires_reassignment"] is False
        assert len(validation["warnings"]) == 0
        assert len(validation["errors"]) == 0

    def test_toggle_active_inactive_to_active(self):
        """Test: Activar categoría inactiva"""
        self.inactive_category.is_active = False
        self.inactive_category.save()

        updated = CategoryService.toggle_active(self.inactive_category)
        assert updated.is_active is True

    def test_toggle_active_active_to_inactive(self):
        """Test: Desactivar categoría activa"""
        updated = CategoryService.toggle_active(self.category1)
        assert updated.is_active is False

    def test_bulk_update_order_empty_list(self):
        """Test: Actualizar orden con lista vacía"""
        updated_count = CategoryService.bulk_update_order(self.user, [])
        assert updated_count == 0

    def test_create_default_categories_creates_both_types(self):
        """Test: create_default_categories crea categorías de ingresos y gastos"""
        new_user = User.objects.create_user(
            identification="11111111",
            username="newuser2",
            email="new2@example.com",
            password="testpass123",
            is_verified=True,
        )

        created = CategoryService.create_default_categories(new_user)
        # Debe crear categorías de ambos tipos
        income_count = sum(1 for cat in created if cat.type == Category.INCOME)
        expense_count = sum(1 for cat in created if cat.type == Category.EXPENSE)
        assert income_count > 0
        assert expense_count > 0
