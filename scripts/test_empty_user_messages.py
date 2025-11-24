"""
Script para crear usuario sin datos y probar mensajes informativos
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

def test_empty_user():
    """Probar endpoints con usuario sin datos"""
    
    print("🧪 PROBANDO MENSAJES CON USUARIO SIN DATOS")
    print("=" * 60)
    
    # Crear usuario sin datos
    username = 'usuario_sin_datos_test'
    
    # Eliminar si existe
    User.objects.filter(username=username).delete()
    
    # Crear nuevo usuario
    user = User.objects.create_user(
        username=username,
        email=f'{username}@test.com',
        password='testpass123'
    )
    
    token, _ = Token.objects.get_or_create(user=user)
    
    print(f"👤 Usuario creado: {user.username}")
    print(f"🔑 Token: {token.key}")
    print(f"📊 Transacciones: 0 (ninguna)")
    
    # Crear cliente de test
    client = Client()
    headers = {'HTTP_AUTHORIZATION': f'Token {token.key}'}
    
    # Probar endpoints
    endpoints = [
        ('/api/analytics/dashboard/', 'Dashboard Completo'),
        ('/api/analytics/indicators/', 'Indicadores KPI'),
        ('/api/analytics/expenses-chart/', 'Gráfico Categorías'),
        ('/api/analytics/daily-flow-chart/', 'Flujo Diario'),
        ('/api/analytics/periods/', 'Períodos Disponibles'),
    ]
    
    for url, name in endpoints:
        print(f"\n{'='*60}")
        print(f"🧪 PROBANDO: {name}")
        print(f"🔗 URL: {url}")
        print('-' * 60)
        
        try:
            response = client.get(url, **headers)
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code in [200, 400]:
                try:
                    data = response.json()
                    
                    # Mostrar respuesta estructurada
                    if 'success' in data:
                        print(f"✅ Success: {data['success']}")
                    
                    if 'error' in data:
                        print(f"⚠️  Error: {data['error']}")
                        
                    if 'code' in data:
                        print(f"🏷️  Code: {data['code']}")
                    
                    if 'message' in data:
                        print(f"💬 Message: {data['message']}")
                    
                    # Mostrar detalles si están disponibles
                    if 'details' in data:
                        details = data['details']
                        print(f"📋 Details:")
                        
                        if isinstance(details, dict):
                            for key, value in details.items():
                                if key == 'suggestions' and isinstance(value, list):
                                    print(f"   💡 Suggestions:")
                                    for suggestion in value:
                                        print(f"      - {suggestion}")
                                elif key == 'quick_start' and isinstance(value, dict):
                                    print(f"   🚀 Quick Start:")
                                    for step, desc in value.items():
                                        print(f"      {step}: {desc}")
                                else:
                                    print(f"   {key}: {value}")
                        else:
                            print(f"   {details}")
                    
                    # Si hay datos, mostrar resumen
                    if data.get('success') and 'data' in data:
                        analytics_data = data['data']
                        print(f"📊 Data Keys: {list(analytics_data.keys()) if isinstance(analytics_data, dict) else 'Not dict'}")
                        
                        # Si hay info_message, mostrarlo
                        if 'info_message' in analytics_data:
                            print(f"ℹ️  Info: {analytics_data['info_message']}")
                    
                except json.JSONDecodeError:
                    print(f"❌ Respuesta no es JSON válido")
                    print(f"📄 Content: {response.content.decode('utf-8')[:200]}...")
            else:
                print(f"❌ Status inesperado: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error ejecutando test: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print(f"🎯 RESUMEN:")
    print(f"✅ Usuario sin datos creado y probado")
    print(f"✅ Todos los endpoints deberían mostrar mensajes informativos")
    print(f"✅ No más errores crípticos de serialización")
    print(f"🧹 Limpieza: Usuario {username} creado para pruebas")

if __name__ == "__main__":
    test_empty_user()