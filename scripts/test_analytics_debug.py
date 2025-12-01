"""
Script de debug para analytics - HU-13
Verificar datos y posibles errores en el servicio de analytics
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "finanzas_back.settings")
django.setup()

from datetime import datetime, date, timedelta
from django.contrib.auth import get_user_model
from transactions.models import Transaction
from categories.models import Category
from analytics.services import FinancialAnalyticsService

User = get_user_model()


def test_analytics_debug():
    """Debuggear el servicio de analytics paso a paso"""

    print("🔍 DEBUGGING ANALYTICS SERVICE")
    print("=" * 50)

    # 1. Verificar usuarios existentes
    print("\n1. USUARIOS EN EL SISTEMA:")
    users = User.objects.all()
    for user in users:
        print(f"   - Usuario ID {user.id}: {user.username}")

    if not users.exists():
        print("   ❌ No hay usuarios en el sistema")
        return

    # Buscar un usuario con transacciones
    user = None
    for u in users:
        tx_count = Transaction.objects.filter(user=u).count()
        print(f"      Usuario {u.username}: {tx_count} transacciones")
        if tx_count > 0 and user is None:
            user = u

    if user is None:
        print("   ❌ No hay usuarios con transacciones")
        return

    print(f"\n🎯 Usando usuario: {user.username} (ID: {user.id})")

    # 2. Verificar transacciones
    print(f"\n2. TRANSACCIONES DEL USUARIO {user.username}:")
    transactions = Transaction.objects.filter(user=user)
    print(f"   - Total transacciones: {transactions.count()}")

    # Transacciones por tipo
    income_count = transactions.filter(type=1).count()
    expense_count = transactions.filter(type=2).count()
    transfer_count = transactions.filter(type=3).count()

    print(f"   - Ingresos (tipo 1): {income_count}")
    print(f"   - Gastos (tipo 2): {expense_count}")
    print(f"   - Transferencias (tipo 3): {transfer_count}")

    if expense_count == 0:
        print("   ❌ No hay gastos para analizar")
        return

    # 3. Verificar categorías
    print(f"\n3. CATEGORÍAS DEL USUARIO:")
    categories = Category.objects.filter(user=user)
    print(f"   - Total categorías: {categories.count()}")

    for category in categories:
        tx_count = transactions.filter(category=category, type=2).count()
        print(f"   - {category.name} (ID: {category.id}): {tx_count} gastos")

    # Gastos sin categoría
    uncategorized_count = transactions.filter(category__isnull=True, type=2).count()
    print(f"   - Sin categoría: {uncategorized_count} gastos")

    # 4. Probar el servicio con período actual
    print(f"\n4. PROBANDO SERVICIO ANALYTICS:")

    try:
        # Período del mes actual
        today = date.today()
        start_date = date(today.year, today.month, 1)
        end_date = today

        print(f"   - Período: {start_date} a {end_date}")

        # Probar get_expenses_by_category
        print(f"\n   🧪 Probando get_expenses_by_category...")

        expenses_data = FinancialAnalyticsService.get_expenses_by_category(
            user=user, start_date=start_date, end_date=end_date, mode="total", others_threshold=0.05
        )

        print(f"   ✅ Resultado del servicio:")
        print(f"      - Total gastos: {expenses_data.get('total_expenses', 'N/A')}")
        print(f"      - Categorías principales: {len(expenses_data.get('chart_data', []))}")
        print(f"      - Categorías en 'otros': {len(expenses_data.get('others_data', []))}")
        print(f"      - Sin categoría: {expenses_data.get('uncategorized_amount', 'N/A')}")
        print(f"      - Total categorías: {expenses_data.get('categories_count', 'N/A')}")
        print(f"      - Modo: {expenses_data.get('mode', 'N/A')}")
        print(f"      - Resumen período: {expenses_data.get('period_summary', 'N/A')}")

        # Mostrar estructura completa
        print(f"\n   📋 ESTRUCTURA COMPLETA:")
        for key, value in expenses_data.items():
            print(f"      {key}: {type(value)} = {value}")

        # Probar indicadores
        print(f"\n   🧪 Probando get_period_indicators...")

        indicators = FinancialAnalyticsService.get_period_indicators(
            user=user, start_date=start_date, end_date=end_date, mode="total"
        )

        print(f"   ✅ Indicadores obtenidos:")
        print(f"      - Ingresos: {indicators.get('income', {}).get('amount', 'N/A')}")
        print(f"      - Gastos: {indicators.get('expenses', {}).get('amount', 'N/A')}")
        print(f"      - Balance: {indicators.get('balance', {}).get('amount', 'N/A')}")

    except Exception as e:
        print(f"   ❌ Error en el servicio: {str(e)}")
        import traceback

        print(f"   📍 Traceback:")
        traceback.print_exc()


if __name__ == "__main__":
    test_analytics_debug()
