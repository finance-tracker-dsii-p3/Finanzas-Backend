# Script de prueba rápida para API de Accounts
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

# 1. Registrar usuario de prueba
print("1. Registrando usuario de prueba...")
register_data = {
    "email": "test@example.com",
    "password": "Test123456!",
    "first_name": "Test",
    "last_name": "User",
}

response = requests.post(f"{BASE_URL}/api/auth/register/", json=register_data)
print(f"   Status: {response.status_code}")

# 2. Login
print("\n2. Haciendo login...")
login_data = {"email": "test@example.com", "password": "Test123456!"}

response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
print(f"   Status: {response.status_code}")

if response.status_code == 200:
    token = response.json().get("token")
    print(f"   Token obtenido: {token[:20]}...")

    headers = {"Authorization": f"Token {token}", "Content-Type": "application/json"}

    # 3. Crear cuenta
    print("\n3. Creando cuenta de ahorros...")
    account_data = {
        "name": "Cuenta Ahorros Test",
        "description": "Cuenta de prueba",
        "account_type": "asset",
        "category": "savings_account",
        "current_balance": "1000000.00",
        "currency": "COP",
    }

    response = requests.post(f"{BASE_URL}/api/accounts/", json=account_data, headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        print(f"   Cuenta creada: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"   Error: {response.text}")

    # 4. Listar cuentas
    print("\n4. Listando cuentas...")
    response = requests.get(f"{BASE_URL}/api/accounts/", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        accounts = response.json()
        print(f"   Total de cuentas: {len(accounts)}")
        for acc in accounts:
            print(f"   - {acc['name']}: {acc['current_balance']} {acc['currency']}")

    # 5. Resumen financiero
    print("\n5. Obteniendo resumen financiero...")
    response = requests.get(f"{BASE_URL}/api/accounts/summary/", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        summary = response.json()
        print(f"   Activos: {summary['total_assets']}")
        print(f"   Pasivos: {summary['total_liabilities']}")
        print(f"   Patrimonio neto: {summary['net_worth']}")

else:
    print(f"   Error en login: {response.text}")
