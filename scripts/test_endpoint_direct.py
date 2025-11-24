"""
Script para probar el endpoint de analytics directamente
"""
import os
import sys
import django
import requests
import json

# No configurar Django aquí para simular petición externa

def test_endpoint():
    """Probar endpoint de analytics con requests"""
    
    print("🧪 PROBANDO ENDPOINT ANALYTICS DIRECTAMENTE")
    print("=" * 50)
    
    # Configuración
    base_url = "http://localhost:8000"
    token = "f707986d59f49eca32683bc45b8f18d59662f75c"
    
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    # URL del endpoint
    url = f"{base_url}/api/analytics/dashboard/"
    
    print(f"🔗 URL: {url}")
    print(f"🔑 Token: {token}")
    
    try:
        # Hacer petición
        print(f"\n📡 Enviando petición...")
        
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print(f"✅ ¡ÉXITO!")
            data = response.json()
            print(f"🎉 Respuesta recibida:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
        else:
            print(f"❌ ERROR - Status: {response.status_code}")
            
            try:
                error_data = response.json()
                print(f"📄 Respuesta de error:")
                print(json.dumps(error_data, indent=2, ensure_ascii=False))
                
                # Si hay traceback, mostrarlo más legible
                if 'details' in error_data and 'traceback' in error_data['details']:
                    print(f"\n🔍 TRACEBACK:")
                    print(error_data['details']['traceback'])
                    
            except:
                print(f"📄 Respuesta (texto):")
                print(response.text)
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Error de conexión: El servidor no está ejecutándose en {base_url}")
        print(f"💡 Asegúrate de ejecutar: python manage.py runserver")
        
    except requests.exceptions.Timeout:
        print(f"❌ Timeout: El servidor no respondió en 10 segundos")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_endpoint()