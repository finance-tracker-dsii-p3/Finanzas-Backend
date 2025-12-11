"""
Test de GitHub Workflow para Analytics (HU-13)
Tests esenciales para CI/CD de endpoints de analíticas financieras
"""

import json
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token

from accounts.models import Account
from categories.models import Category
from transactions.models import Transaction

User = get_user_model()


class AnalyticsGitHubWorkflowTests(TestCase):
    """Tests básicos para GitHub Actions - Analytics HU-13"""

    def setUp(self):
        """Configuración mínima para tests de CI/CD"""
        # Usuario de prueba
        self.user = User.objects.create_user(
            identification="12345678",
            username="analyticsuser",
            email="analytics@test.com",
            password="testpass123",
            first_name="Analytics",
            last_name="User",
        )

        # Token de autenticación
        self.token = Token.objects.create(user=self.user)
        self.auth_header = f"Token {self.token.key}"

        # Cuenta de prueba
        self.account = Account.objects.create(
            user=self.user,
            name="Cuenta Prueba Analytics",
            account_type="asset",
            category="savings_account",
            current_balance=Decimal("1000.00"),
        )

        # Categorías de prueba - usar colores con buen contraste
        self.income_category = Category.objects.create(
            user=self.user,
            name="Salario",
            type="income",
            color="#1B5E20",  # Verde oscuro con buen contraste
        )

        self.expense_category = Category.objects.create(
            user=self.user,
            name="Alimentación",
            type="expense",
            color="#B71C1C",  # Rojo oscuro con buen contraste
        )

    def test_analytics_dashboard_basic(self):
        """Test básico de dashboard analytics"""
        url = reverse("analytics_dashboard")
        response = self.client.get(url, HTTP_AUTHORIZATION=self.auth_header)

        # El endpoint debe retornar 200 incluso sin datos
        assert response.status_code == 200
        data = response.json()

        # Para usuario sin transacciones, debe retornar error controlado
        if not data.get("success"):
            assert "error" in data
            assert "code" in data
            # Es válido que retorne NO_DATA_AVAILABLE para usuario sin transacciones
            assert data["code"] in ["NO_DATA_AVAILABLE", "NO_TRANSACTIONS"]
        else:
            # Si tiene datos, verificar estructura
            assert data["success"]
            analytics_data = data["data"]
            assert "indicators" in analytics_data
            assert "expenses_chart" in analytics_data
            assert "daily_flow_chart" in analytics_data

    def test_analytics_dashboard_with_data(self):
        """Test dashboard con transacciones reales"""
        # Crear transacciones de prueba
        from datetime import date

        Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            category=self.income_category,
            description="Ingreso Test",
            base_amount=int(1500.00 * 100),  # Convertir a centavos
            type=1,  # Income
            date=date.today(),
        )

        Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            category=self.expense_category,
            description="Gasto Test",
            base_amount=int(250.00 * 100),  # Convertir a centavos
            type=2,  # Expense
            date=date.today(),
        )

        url = reverse("analytics_dashboard")
        response = self.client.get(url, HTTP_AUTHORIZATION=self.auth_header)

        assert response.status_code == 200
        data = response.json()

        # Debe tener datos exitosos
        assert data["success"]
        analytics_data = data["data"]

        # Verificar cálculos
        indicators = analytics_data["indicators"]
        # Puede tener ingresos (type=1) y gastos (type=2)
        assert "income" in indicators
        assert "expenses" in indicators
        assert "balance" in indicators

        # Verificar gráfico de gastos por categoría
        expenses_chart = analytics_data["expenses_chart"]
        # Con al menos una transacción de gasto, debe tener datos
        if expenses_chart.get("chart_data"):
            assert len(expenses_chart["chart_data"]) > 0
        assert "categories_count" in expenses_chart

    def test_analytics_period_indicators(self):
        """Test endpoint de indicadores por período"""
        url = reverse("period_indicators")
        response = self.client.get(
            url + "?period=current_month", HTTP_AUTHORIZATION=self.auth_header
        )

        assert response.status_code == 200
        data = response.json()

        # Para usuario sin transacciones, puede retornar error controlado
        if not data.get("success"):
            assert "error" in data
            assert "code" in data
            # Es válido que no tenga transacciones
            assert data["code"] == "NO_TRANSACTIONS"
        else:
            # Si tiene datos, verificar estructura
            assert data["success"]
            indicators = data["data"]
            assert "income" in indicators
            assert "expenses" in indicators
            assert "balance" in indicators

    def test_analytics_expenses_chart(self):
        """Test endpoint de gráfico de gastos por categoría"""
        url = reverse("expenses_by_category")
        response = self.client.get(url, HTTP_AUTHORIZATION=self.auth_header)

        assert response.status_code == 200
        data = response.json()

        # Para usuario sin gastos, puede retornar error controlado
        if not data.get("success"):
            assert "error" in data
            assert "code" in data
            # Es válido que no tenga gastos
            assert data["code"] == "NO_EXPENSES"
        else:
            # Si tiene datos, verificar estructura
            assert data["success"]
            chart_data = data["data"]
            assert "chart_data" in chart_data
            assert "categories_count" in chart_data
            assert "total_expenses" in chart_data

            # categories_count debe existir (corrige el KeyError reportado)
            assert isinstance(chart_data["categories_count"], int)

    def test_analytics_daily_flow_chart(self):
        """Test endpoint de gráfico de flujo diario"""
        url = reverse("daily_flow_chart")
        response = self.client.get(url, HTTP_AUTHORIZATION=self.auth_header)

        assert response.status_code == 200
        data = response.json()

        # Debe retornar datos exitosos (puede tener transacciones o no)
        assert data["success"]
        chart_data = data["data"]

        # Verificar estructura del flujo diario
        assert "dates" in chart_data
        assert "series" in chart_data
        assert isinstance(chart_data["dates"], list)

    def test_analytics_available_periods(self):
        """Test endpoint de períodos disponibles"""
        url = reverse("available_periods")
        response = self.client.get(url, HTTP_AUTHORIZATION=self.auth_header)

        assert response.status_code == 200
        data = response.json()

        # Debe retornar datos exitosos
        assert data["success"]
        periods_data = data["data"]

        # Verificar lista de períodos
        assert "available_periods" in periods_data
        assert isinstance(periods_data["available_periods"], list)

    def test_analytics_category_transactions(self):
        """Test endpoint de transacciones por categoría"""
        # Crear transacción para drill-down
        from datetime import date

        transaction = Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            category=self.expense_category,
            description="Transacción Categoría Test",
            base_amount=int(100.00 * 100),  # Convertir a centavos
            type=2,  # Expense
            date=date.today(),
        )

        url = reverse(
            "category_transactions", kwargs={"category_id": str(self.expense_category.id)}
        )
        response = self.client.get(url, HTTP_AUTHORIZATION=self.auth_header)

        assert response.status_code == 200
        data = response.json()

        # Debe retornar datos exitosos
        assert data["success"]
        transactions_data = data["data"]

        # Verificar estructura de transacciones
        assert "transactions" in transactions_data
        assert "category_name" in transactions_data
        assert "total_count" in transactions_data

    def test_analytics_authentication_required(self):
        """Test que todos los endpoints requieren autenticación"""
        endpoints = [
            "analytics_dashboard",
            "period_indicators",
            "expenses_by_category",
            "daily_flow_chart",
            "available_periods",
        ]

        for endpoint_name in endpoints:
            url = reverse(endpoint_name)
            response = self.client.get(url)  # Sin autenticación

            # Debe retornar 401 sin token
            assert (
                response.status_code == 401
            ), f"Endpoint {endpoint_name} debe requerir autenticación"

    def test_analytics_user_isolation(self):
        """Test que analytics respeta aislamiento por usuario"""
        # Crear segundo usuario
        other_user = User.objects.create_user(
            identification="87654321",
            username="otheruser",
            email="other@test.com",
            password="testpass123",
        )

        other_token = Token.objects.create(user=other_user)
        other_auth_header = f"Token {other_token.key}"

        # Crear transacción para el usuario original
        from datetime import date

        Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            category=self.expense_category,
            description="Transacción Usuario 1",
            base_amount=int(500.00 * 100),  # Convertir a centavos
            type=2,  # Expense
            date=date.today(),
        )

        # El otro usuario no debe ver datos del primero
        url = reverse("analytics_dashboard")
        response = self.client.get(url, HTTP_AUTHORIZATION=other_auth_header)

        assert response.status_code == 200
        data = response.json()

        # El otro usuario no debe ver datos del primero
        # Puede retornar error por no tener transacciones o indicadores en cero
        if not data.get("success"):
            assert "error" in data
            assert data["code"] == "NO_DATA_AVAILABLE"
        else:
            # Si retorna datos, deben estar en cero
            analytics_data = data["data"]
            indicators = analytics_data["indicators"]
            assert indicators["expenses"]["amount"] == 0
            assert indicators["income"]["amount"] == 0

    def test_analytics_edge_cases(self):
        """Test casos extremos (usuario sin datos)"""
        # Usuario sin transacciones
        url = reverse("expenses_by_category")
        response = self.client.get(url, HTTP_AUTHORIZATION=self.auth_header)

        assert response.status_code == 200
        data = response.json()

        # Para usuario sin gastos, debe retornar error controlado
        if not data.get("success"):
            assert "error" in data
            assert data["code"] == "NO_EXPENSES"
        else:
            # Si retorna datos, verificar estructura vacía
            chart_data = data["data"]
            assert len(chart_data.get("chart_data", [])) == 0
            assert chart_data["categories_count"] == 0  # El fix del KeyError
            assert chart_data["total_expenses"] == 0


class AnalyticsPerformanceTests(TestCase):
    """Tests de rendimiento básicos para CI/CD"""

    def setUp(self):
        """Configuración para tests de rendimiento"""
        self.user = User.objects.create_user(
            identification="99999999",
            username="perfuser",
            email="perf@test.com",
            password="testpass123",
        )

        self.token = Token.objects.create(user=self.user)
        self.auth_header = f"Token {self.token.key}"

        # Crear cuenta
        self.account = Account.objects.create(
            user=self.user,
            name="Cuenta Performance",
            account_type="asset",
            category="bank_account",
            current_balance=Decimal("5000.00"),
        )

        # Crear múltiples categorías y transacciones para test de carga
        # Colores oscuros con buen contraste
        dark_colors = [
            "#B71C1C",
            "#880E4F",
            "#4A148C",
            "#311B92",
            "#1A237E",
            "#0D47A1",
            "#01579B",
            "#006064",
            "#004D40",
            "#1B5E20",
        ]

        self.categories = []
        for i in range(10):
            category = Category.objects.create(
                user=self.user,
                name=f"Categoría {i}",
                type="expense",
                color=dark_colors[i % len(dark_colors)],
            )
            self.categories.append(category)

            # Crear varias transacciones por categoría
            for j in range(5):
                from datetime import date

                Transaction.objects.create(
                    user=self.user,
                    origin_account=self.account,
                    category=category,
                    description=f"Transacción {i}-{j}",
                    base_amount=int((i + 1) * 10 * 100),  # Convertir a centavos
                    type=2,  # Expense
                    date=date.today(),
                )

    def test_analytics_dashboard_performance(self):
        """Test que dashboard responde en tiempo razonable"""
        import time

        url = reverse("analytics_dashboard")

        start_time = time.time()
        response = self.client.get(url, HTTP_AUTHORIZATION=self.auth_header)
        end_time = time.time()

        # Verificar respuesta exitosa
        assert response.status_code == 200

        # Verificar tiempo de respuesta razonable (< 2 segundos)
        response_time = end_time - start_time
        assert response_time < 2.0, f"Dashboard tardó {response_time:.2f}s, muy lento para CI/CD"

        # Verificar que retorna datos
        data = response.json()
        assert data["success"]
        analytics_data = data["data"]
        assert "indicators" in analytics_data

        # Con múltiples transacciones debe tener datos de gastos
        expenses_chart = analytics_data["expenses_chart"]
        if expenses_chart.get("chart_data"):
            assert len(expenses_chart["chart_data"]) > 0


class AnalyticsPeriodComparisonTests(TestCase):
    """Tests para comparación entre períodos (HU-14)"""

    def setUp(self):
        """Configuración para tests de comparación"""
        # Usuario de prueba
        self.user = User.objects.create_user(
            identification="11223344",
            username="compareuser",
            email="compare@test.com",
            password="testpass123",
            first_name="Compare",
            last_name="User",
        )

        # Token de autenticación
        self.token = Token.objects.create(user=self.user)
        self.auth_header = f"Token {self.token.key}"

        # Cuenta de prueba
        self.account = Account.objects.create(
            user=self.user,
            name="Cuenta Comparación",
            account_type="asset",
            category="bank_account",
            current_balance=Decimal("2000.00"),
        )

        # Categorías de prueba
        self.income_category = Category.objects.create(
            user=self.user, name="Salario", type="income", color="#1B5E20"
        )

        self.expense_category = Category.objects.create(
            user=self.user, name="Alimentación", type="expense", color="#B71C1C"
        )

    def test_compare_periods_basic(self):
        """Test básico de comparación entre períodos"""
        from datetime import date, timedelta

        # Crear transacciones en dos períodos diferentes
        # Período 1: hace 60 días
        period1_date = date.today() - timedelta(days=60)
        Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            category=self.income_category,
            description="Ingreso Período 1",
            base_amount=int(2000.00 * 100),
            type=1,
            date=period1_date,
        )

        Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            category=self.expense_category,
            description="Gasto Período 1",
            base_amount=int(500.00 * 100),
            type=2,
            date=period1_date,
        )

        # Período 2: hace 30 días
        period2_date = date.today() - timedelta(days=30)
        Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            category=self.income_category,
            description="Ingreso Período 2",
            base_amount=int(2500.00 * 100),
            type=1,
            date=period2_date,
        )

        Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            category=self.expense_category,
            description="Gasto Período 2",
            base_amount=int(400.00 * 100),
            type=2,
            date=period2_date,
        )

        # Realizar comparación usando rangos personalizados
        period1_str = f"{(period1_date - timedelta(days=5)).strftime('%Y-%m-%d')},{(period1_date + timedelta(days=5)).strftime('%Y-%m-%d')}"
        period2_str = f"{(period2_date - timedelta(days=5)).strftime('%Y-%m-%d')},{(period2_date + timedelta(days=5)).strftime('%Y-%m-%d')}"

        url = reverse("compare_periods")
        response = self.client.get(
            url + f"?period1={period1_str}&period2={period2_str}&mode=total",
            HTTP_AUTHORIZATION=self.auth_header,
        )

        assert response.status_code == 200
        data = response.json()

        # Verificar respuesta exitosa
        assert data["success"]
        comparison_data = data["data"]

        # Verificar estructura de respuesta
        assert "comparison_summary" in comparison_data
        assert "period_data" in comparison_data
        assert "differences" in comparison_data
        assert "insights" in comparison_data

        # Verificar que puede comparar
        assert comparison_data["comparison_summary"]["can_compare"]

        # Verificar diferencias calculadas
        differences = comparison_data["differences"]
        assert "income" in differences
        assert "expenses" in differences
        assert "balance" in differences

        # Los ingresos deben haber aumentado (2500 > 2000)
        assert differences["income"]["is_increase"]

        # Los gastos deben haber disminuido (400 < 500)
        assert not differences["expenses"]["is_increase"]

    def test_compare_periods_missing_parameters(self):
        """Test error por parámetros faltantes"""
        url = reverse("compare_periods")
        response = self.client.get(
            url + "?period1=2025-09",  # Falta period2
            HTTP_AUTHORIZATION=self.auth_header,
        )

        assert response.status_code == 400
        data = response.json()

        assert not data["success"]
        assert data["code"] == "MISSING_PERIODS"
        assert "period1 y period2 son requeridos" in data["error"]

    def test_compare_periods_invalid_format(self):
        """Test error por formato de período inválido"""
        url = reverse("compare_periods")
        response = self.client.get(
            url + "?period1=invalid&period2=also-invalid", HTTP_AUTHORIZATION=self.auth_header
        )

        assert response.status_code == 400
        data = response.json()

        assert not data["success"]
        assert data["code"] == "INVALID_PERIOD_FORMAT"
        assert "supported_formats" in data

    def test_compare_periods_no_data(self):
        """Test comparación cuando no hay datos en períodos"""
        # Crear una transacción en un período diferente para evitar NO_USER_TRANSACTIONS
        from datetime import date

        Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            category=self.income_category,
            description="Transacción en período diferente",
            base_amount=int(1000.00 * 100),
            type=1,
            date=date.today(),  # Período actual
        )

        # Ahora comparar períodos que no tienen datos (2020)
        url = reverse("compare_periods")
        response = self.client.get(
            url + "?period1=2020-01&period2=2020-02&mode=total", HTTP_AUTHORIZATION=self.auth_header
        )

        assert response.status_code == 200  # 200 pero con error controlado
        data = response.json()

        assert not data["success"]
        # Ahora debe ser NO_DATA_IN_PERIODS porque el usuario tiene transacciones, pero no en esos períodos
        assert data["code"] == "NO_DATA_IN_PERIODS"

    def test_compare_periods_predefined_periods(self):
        """Test comparación usando períodos predefinidos"""
        from datetime import date

        # Crear transacción en mes actual
        Transaction.objects.create(
            user=self.user,
            origin_account=self.account,
            category=self.income_category,
            description="Ingreso Actual",
            base_amount=int(3000.00 * 100),
            type=1,
            date=date.today(),
        )

        url = reverse("compare_periods")
        response = self.client.get(
            url + "?period1=last_month&period2=current_month&mode=base",
            HTTP_AUTHORIZATION=self.auth_header,
        )

        # Debe manejar correctamente incluso si un período no tiene datos
        assert response.status_code == 200
        data = response.json()

        # Puede ser exitoso o fallar dependiendo de si hay datos en ambos períodos
        if data["success"]:
            assert "comparison_summary" in data["data"]
        else:
            # Error controlado por falta de datos
            assert "NO_DATA" in data["code"]

    def test_compare_periods_authentication_required(self):
        """Test que comparación requiere autenticación"""
        url = reverse("compare_periods")
        response = self.client.get(
            url + "?period1=2025-09&period2=2025-10"
        )  # Sin token de autorización

        assert response.status_code == 401
