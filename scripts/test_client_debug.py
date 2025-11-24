"""
Test usando Django TestClient para simular petición real
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finanzas_back.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
import json

User = get_user_model()

def test_with_client():
    """Probar endpoint usando Django TestClient"""
    
    print("🧪 PROBANDO CON DJANGO TEST CLIENT")
    print("=" * 50)
    
    # Crear cliente
    client = Client()
    
    # Obtener usuario y token
    user = User.objects.filter(username='usuarioPrueba').first()
    if not user:
        print("❌ Usuario 'usuarioPrueba' no encontrado")
        return
    
    token, _ = Token.objects.get_or_create(user=user)
    
    print(f"👤 Usuario: {user.username}")
    print(f"🔑 Token: {token.key}")
    
    # Headers para autenticación
    headers = {
        'HTTP_AUTHORIZATION': f'Token {token.key}'
    }
    
    # URL del endpoint
    url = '/api/analytics/dashboard/'
    
    print(f"🔗 URL: {url}")
    
    try:
        # Hacer petición
        print(f"\n📡 Enviando petición...")
        
        response = client.get(url, **headers)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📋 Content-Type: {response.get('Content-Type', 'N/A')}")
        
        if response.status_code == 200:
            print(f"✅ ¡ÉXITO!")
            
            # Intentar parsear JSON
            try:
                data = response.json()
                print(f"🎉 Respuesta JSON válida:")
                
                # Mostrar estructura resumida
                if 'success' in data:
                    print(f"   - Success: {data['success']}")
                if 'data' in data:
                    print(f"   - Data keys: {list(data['data'].keys()) if isinstance(data['data'], dict) else 'No es dict'}")
                if 'message' in data:
                    print(f"   - Message: {data['message']}")
                    
                # Verificar estructura específica
                if data.get('success') and 'data' in data:
                    analytics_data = data['data']
                    print(f"\n📊 ANÁLISIS DE LA RESPUESTA:")
                    
                    if 'expenses_chart' in analytics_data:
                        expenses = analytics_data['expenses_chart']
                        print(f"   ✅ expenses_chart presente")
                        print(f"      - Tipo: {type(expenses)}")
                        print(f"      - Claves: {list(expenses.keys()) if isinstance(expenses, dict) else 'No es dict'}")
                        
                        if 'categories_count' in expenses:
                            print(f"      ✅ categories_count: {expenses['categories_count']}")
                        else:
                            print(f"      ❌ categories_count FALTANTE")
                            print(f"      📋 Claves disponibles: {list(expenses.keys())}")
                    else:
                        print(f"   ❌ expenses_chart FALTANTE")
                
            except json.JSONDecodeError as e:
                print(f"❌ Error parseando JSON: {e}")
                print(f"📄 Contenido raw (primeros 500 chars):")
                print(response.content.decode('utf-8')[:500])
                
        else:
            print(f"❌ ERROR - Status: {response.status_code}")
            
            try:
                if hasattr(response, 'json'):
                    error_data = response.json()
                    print(f"📄 Respuesta de error:")
                    print(json.dumps(error_data, indent=2, ensure_ascii=False))
                    
                    # Si hay traceback, mostrarlo
                    if isinstance(error_data, dict) and 'details' in error_data:
                        details = error_data['details']
                        if 'traceback' in details:
                            print(f"\n🔍 TRACEBACK COMPLETO:")
                            print(details['traceback'])
                else:
                    print(f"📄 Respuesta (texto):")
                    print(response.content.decode('utf-8'))
                    
            except Exception as parse_error:
                print(f"❌ Error parseando respuesta de error: {parse_error}")
                print(f"📄 Contenido raw:")
                print(response.content.decode('utf-8'))
                
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_client()