#!/usr/bin/env python
"""
Script para probar los nuevos mensajes de error mejorados de la API de reglas
"""
import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"
TOKEN = "Token 123invalidtoken"  # Token inválido para mostrar error 401

def test_error_messages():
    """Probar diferentes tipos de errores"""
    
    headers = {
        'Authorization': TOKEN,
        'Content-Type': 'application/json'
    }
    
    print("🧪 PRUEBAS DE MENSAJES DE ERROR MEJORADOS")
    print("=" * 50)
    
    # 1. Test error 401 - Token inválido
    print("\n1️⃣ Test Error 401 - Token inválido:")
    response = requests.get(f"{BASE_URL}/api/rules/", headers=headers)
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response (text): {response.text}")
    
    # 2. Test error 400 - Datos inválidos (sin token válido, pero mostrará estructura)
    print("\n2️⃣ Test Error 400 - Datos inválidos:")
    invalid_data = {
        "name": "",  # Nombre vacío
        "criteria_type": "invalid_type",  # Tipo inválido
        "action_type": "assign_category"  # Sin target_category
    }
    response = requests.post(f"{BASE_URL}/api/rules/", 
                           headers=headers, 
                           json=invalid_data)
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response (text): {response.text}")
    
    # 3. Test error 404 - Recurso no encontrado
    print("\n3️⃣ Test Error 404 - Regla no existente:")
    response = requests.get(f"{BASE_URL}/api/rules/999999/", headers=headers)
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response (text): {response.text}")
    
    print("\n✅ PRUEBAS COMPLETADAS")
    print("\nLos errores ahora deben mostrar:")
    print("- Mensajes claros y específicos")
    print("- Sugerencias de solución")
    print("- Formato JSON consistente")
    print("- Información de debugging útil")

if __name__ == "__main__":
    test_error_messages()