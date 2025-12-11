"""
Probar creación de transacción con datos correctos usando Django TestClient
"""

import os
import sys

import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "finanzas_back.settings")
django.setup()

import json

from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework.authtoken.models import Token

from accounts.models import Account

User = get_user_model()


def test_transaction_creation():
    """Probar creación de transacción con datos correctos"""

    print("🧪 PROBANDO CREACIÓN DE TRANSACCIÓN")
    print("=" * 50)

    # Crear cliente
    client = Client()

    # Obtener usuario y token
    user = User.objects.filter(username="usuarioPrueba").first()
    if not user:
        print("❌ Usuario 'usuarioPrueba' no encontrado")
        return

    token, _ = Token.objects.get_or_create(user=user)

    # Headers para autenticación
    headers = {"HTTP_AUTHORIZATION": f"Token {token.key}", "content_type": "application/json"}

    # Obtener primera cuenta disponible
    account = Account.objects.filter(user=user).first()
    if not account:
        print("❌ No hay cuentas disponibles")
        return

    print(f"👤 Usuario: {user.username}")
    print(f"💳 Cuenta: {account.name} (ID: {account.id})")

    # Datos de transacción correctos
    transaction_data = {
        "origin_account": account.id,
        "type": 1,
        "base_amount": 2500000,
        "date": "2025-11-24",
        "description": "Salario mensual",
        "tag": "salario",
    }

    print(f"\n📋 DATOS DE TRANSACCIÓN:")
    print(json.dumps(transaction_data, indent=2))

    try:
        # Hacer petición POST
        response = client.post("/api/transactions/", data=json.dumps(transaction_data), **headers)

        print(f"\n📡 RESULTADO:")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 201:
            print("✅ ¡TRANSACCIÓN CREADA EXITOSAMENTE!")

            result = response.json()
            print(f"\n🎉 TRANSACCIÓN CREADA:")
            print(f"   - ID: {result['id']}")
            print(
                f"   - Tipo: {result['type']} ({['', 'Ingreso', 'Gasto', 'Transferencia', 'Ahorro'][result['type']]})"
            )
            print(f"   - Monto base: ${result['base_amount']:,}")
            print(f"   - Monto total: ${result['total_amount']:,}")
            print(f"   - Fecha: {result['date']}")
            print(f"   - Descripción: {result.get('description', 'N/A')}")
            print(f"   - Etiqueta: {result.get('tag', 'N/A')}")

            if result.get("applied_rule"):
                print(f"   - Regla aplicada: ID {result['applied_rule']}")
            else:
                print(f"   - Regla aplicada: Ninguna")

        else:
            print("❌ ERROR EN LA CREACIÓN")

            try:
                error_data = response.json()
                print(f"\n📄 Respuesta de error:")
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
            except:
                print(f"📄 Respuesta (texto):")
                print(response.content.decode("utf-8"))

    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_transaction_creation()
