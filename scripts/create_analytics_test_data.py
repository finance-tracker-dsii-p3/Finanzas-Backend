"""
Script para crear datos de prueba para analytics - HU-13
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finanzas_back.settings')
django.setup()

from datetime import datetime, date, timedelta
from decimal import Decimal
from django.contrib.auth import get_user_model
from transactions.models import Transaction
from categories.models import Category
from accounts.models import Account

User = get_user_model()

def create_test_data():
    """Crear datos de prueba para analytics"""
    
    print("🏗️ CREANDO DATOS DE PRUEBA PARA ANALYTICS")
    print("=" * 50)
    
    # 1. Obtener usuario de prueba
    user = User.objects.filter(username='usuarioPrueba').first()
    if not user:
        print("❌ Usuario 'usuarioPrueba' no encontrado")
        return
    
    print(f"👤 Usuario: {user.username} (ID: {user.id})")
    
    # 2. Crear cuenta de origen si no existe
    print("\n💳 Creando cuenta de origen...")
    
    account, created = Account.objects.get_or_create(
        user=user,
        name='Cuenta Principal',
        defaults={
            'account_type': Account.ASSET,
            'category': Account.BANK_ACCOUNT,
            'current_balance': Decimal('1000000'),  # Balance inicial
            'description': 'Cuenta principal para pruebas'
        }
    )
    print(f"   {'✅ Creada' if created else '🔄 Existe'}: {account.name}")
    
    # 3. Crear categorías si no existen
    print("\n📂 Creando categorías...")
    
    categories_data = [
        {'name': 'Comida', 'color': '#DC2626', 'icon': 'fa-utensils'},
        {'name': 'Transporte', 'color': '#EA580C', 'icon': 'fa-car'},
        {'name': 'Entretenimiento', 'color': '#C2410C', 'icon': 'fa-film'},
        {'name': 'Salud', 'color': '#059669', 'icon': 'fa-heartbeat'},
        {'name': 'Educación', 'color': '#3B82F6', 'icon': 'fa-graduation-cap'},
    ]
    
    categories = {}
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            user=user,
            name=cat_data['name'],
            defaults={
                'color': cat_data['color'],
                'icon': cat_data['icon']
            }
        )
        categories[cat_data['name']] = category
        print(f"   {'✅ Creada' if created else '🔄 Existe'}: {category.name}")
    
    # 4. Crear transacciones de ejemplo para el mes actual
    print("\n💰 Creando transacciones del mes actual...")
    
    today = date.today()
    
    transactions_data = [
        # Ingresos
        {'date': date(today.year, today.month, 1), 'type': 1, 'description': 'Salario', 'base_amount': 2500000, 'total_amount': 2500000},
        {'date': date(today.year, today.month, 15), 'type': 1, 'description': 'Freelance', 'base_amount': 800000, 'total_amount': 800000},
        
        # Gastos con categoría
        {'date': date(today.year, today.month, 2), 'type': 2, 'description': 'Supermercado', 'base_amount': 150000, 'total_amount': 165000, 'category': 'Comida'},
        {'date': date(today.year, today.month, 3), 'type': 2, 'description': 'Gasolina', 'base_amount': 80000, 'total_amount': 85000, 'category': 'Transporte'},
        {'date': date(today.year, today.month, 5), 'type': 2, 'description': 'Restaurante', 'base_amount': 45000, 'total_amount': 50000, 'category': 'Comida'},
        {'date': date(today.year, today.month, 8), 'type': 2, 'description': 'Cine', 'base_amount': 25000, 'total_amount': 30000, 'category': 'Entretenimiento'},
        {'date': date(today.year, today.month, 10), 'type': 2, 'description': 'Uber', 'base_amount': 15000, 'total_amount': 18000, 'category': 'Transporte'},
        {'date': date(today.year, today.month, 12), 'type': 2, 'description': 'Almuerzo', 'base_amount': 12000, 'total_amount': 14000, 'category': 'Comida'},
        {'date': date(today.year, today.month, 15), 'type': 2, 'description': 'Farmacia', 'base_amount': 35000, 'total_amount': 40000, 'category': 'Salud'},
        {'date': date(today.year, today.month, 18), 'type': 2, 'description': 'Curso online', 'base_amount': 120000, 'total_amount': 140000, 'category': 'Educación'},
        {'date': date(today.year, today.month, 20), 'type': 2, 'description': 'Mercado', 'base_amount': 85000, 'total_amount': 95000, 'category': 'Comida'},
        
        # Gastos sin categoría
        {'date': date(today.year, today.month, 22), 'type': 2, 'description': 'Compra varia', 'base_amount': 50000, 'total_amount': 55000, 'category': None},
        {'date': today, 'type': 2, 'description': 'Gasto varios', 'base_amount': 30000, 'total_amount': 35000, 'category': None},
    ]
    
    created_count = 0
    for tx_data in transactions_data:
        category = None
        if tx_data.get('category'):
            category = categories[tx_data['category']]
        
        # Verificar si ya existe una transacción similar
        existing = Transaction.objects.filter(
            user=user,
            date=tx_data['date'],
            description=tx_data['description'],
            base_amount=tx_data['base_amount']
        ).first()
        
        if not existing:
            Transaction.objects.create(
                user=user,
                origin_account=account,
                date=tx_data['date'],
                type=tx_data['type'],
                description=tx_data['description'],
                base_amount=Decimal(str(tx_data['base_amount'])),
                total_amount=Decimal(str(tx_data['total_amount'])),
                category=category
            )
            created_count += 1
            print(f"   ✅ Creada: {tx_data['description']} - ${tx_data['base_amount']:,}")
        else:
            print(f"   🔄 Existe: {tx_data['description']} - ${tx_data['base_amount']:,}")
    
    print(f"\n📊 RESUMEN:")
    
    # Contar transacciones creadas
    total_tx = Transaction.objects.filter(user=user).count()
    income_tx = Transaction.objects.filter(user=user, type=1).count()
    expense_tx = Transaction.objects.filter(user=user, type=2).count()
    
    print(f"   - Transacciones creadas: {created_count}")
    print(f"   - Total transacciones del usuario: {total_tx}")
    print(f"   - Ingresos: {income_tx}")
    print(f"   - Gastos: {expense_tx}")
    
    # Calcular totales
    total_income = Transaction.objects.filter(user=user, type=1).aggregate(
        total=django.db.models.Sum('base_amount')
    )['total'] or 0
    
    total_expenses = Transaction.objects.filter(user=user, type=2).aggregate(
        total=django.db.models.Sum('base_amount')
    )['total'] or 0
    
    print(f"   - Total ingresos: ${total_income:,}")
    print(f"   - Total gastos: ${total_expenses:,}")
    print(f"   - Balance: ${total_income - total_expenses:,}")
    
    print(f"\n✅ ¡Datos de prueba listos para analytics!")
    print(f"🧪 Ahora puedes probar: GET /api/analytics/dashboard/")

if __name__ == "__main__":
    import django.db.models
    create_test_data()