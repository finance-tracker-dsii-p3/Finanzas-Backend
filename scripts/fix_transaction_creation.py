"""
Script para verificar cuentas disponibles y crear transacción correctamente
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finanzas_back.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Account
from rest_framework.authtoken.models import Token

User = get_user_model()

def check_accounts_and_fix():
    """Verificar cuentas disponibles y mostrar cómo crear transacciones"""
    
    print("🔍 VERIFICANDO CUENTAS DISPONIBLES")
    print("=" * 50)
    
    # Obtener usuario de prueba
    user = User.objects.filter(username='usuarioPrueba').first()
    if not user:
        print("❌ Usuario 'usuarioPrueba' no encontrado")
        return
    
    print(f"👤 Usuario: {user.username} (ID: {user.id})")
    
    # Verificar cuentas del usuario
    accounts = Account.objects.filter(user=user)
    print("\n💳 CUENTAS DISPONIBLES:")
    print(f"   - Total cuentas: {accounts.count()}")
    
    if accounts.exists():
        for account in accounts:
            print(f"   ✅ ID: {account.id} - {account.name} ({account.get_category_display()})")
            print(f"      Balance: ${account.current_balance:,.0f} {account.currency}")
            print(f"      Tipo: {account.get_account_type_display()}")
            print()
        
        # Usar la primera cuenta disponible
        first_account = accounts.first()
        
        print("🧪 EJEMPLO CORRECTO DE TRANSACCIÓN:")
        print(f"   Usar cuenta ID: {first_account.id}")
        
        transaction_example = {
            "origin_account": first_account.id,
            "type": 1,
            "base_amount": 2500000,
            "date": "2025-11-24",
            "description": "Salario mensual",
            "tag": "salario"
        }
        
        print("\n📋 JSON CORREGIDO:")
        import json
        print(json.dumps(transaction_example, indent=2))
        
        # Verificar token
        token, _ = Token.objects.get_or_create(user=user)
        print("\n🔑 TOKEN PARA USAR:")
        print(f"Authorization: Token {token.key}")
        
        print("\n🚀 COMANDO CURL COMPLETO:")
        print('curl -X POST \\')
        print(f'  -H "Authorization: Token {token.key}" \\')
        print('  -H "Content-Type: application/json" \\')
        print(f'  -d \'{json.dumps(transaction_example)}\' \\')
        print('  http://localhost:8000/api/transactions/')
        
    else:
        print("❌ No hay cuentas disponibles para este usuario")
        print("\n💡 SOLUCIÓN:")
        print("1. Crear una cuenta primero:")
        print("   POST /api/accounts/")
        print("2. O usar un usuario que ya tenga cuentas")

if __name__ == "__main__":
    check_accounts_and_fix()