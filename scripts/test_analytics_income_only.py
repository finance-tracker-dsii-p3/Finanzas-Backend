"""
Probar analytics con usuario que solo tiene ingresos (sin gastos)
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

User = get_user_model()


def test_analytics_only_income():
    """Probar analytics con usuario que solo tiene ingresos"""

    print("🧪 PROBANDO ANALYTICS - SOLO INGRESOS")
    print("=" * 50)

    # Crear cliente
    client = Client()

    # Obtener usuario josefilo que solo tiene ingresos
    user = User.objects.filter(username="josefilo").first()
    if not user:
        print("❌ Usuario 'josefilo' no encontrado")
        return

    token, _ = Token.objects.get_or_create(user=user)

    # Headers para autenticación
    headers = {"HTTP_AUTHORIZATION": f"Token {token.key}"}

    print(f"👤 Usuario: {user.username}")
    print(f"🔑 Token: {token.key}")

    try:
        # Hacer petición a analytics
        response = client.get("/api/analytics/dashboard/", **headers)

        print(f"\n📡 RESULTADO:")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✅ ¡ANALYTICS FUNCIONA CON SOLO INGRESOS!")

            result = response.json()
            print(f"\n🎉 RESPUESTA EXITOSA:")
            print(f"   - Success: {result['success']}")
            print(f"   - Message: {result['message']}")

            if "data" in result:
                data = result["data"]

                # Verificar indicadores
                if "indicators" in data:
                    ind = data["indicators"]
                    print(f"\n📊 INDICADORES:")
                    print(f"   - Ingresos: ${ind['income']['amount']:,}")
                    print(f"   - Gastos: ${ind['expenses']['amount']:,}")
                    print(f"   - Balance: ${ind['balance']['amount']:,}")

                # Verificar gráfico de gastos
                if "expenses_chart" in data:
                    exp = data["expenses_chart"]
                    print(f"\n📈 GRÁFICO DE GASTOS:")
                    print(f"   - Total gastos: ${exp['total_expenses']:,}")
                    print(f"   - Categorías principales: {len(exp['chart_data'])}")
                    print(f"   - Categorías en otros: {len(exp['others_data'])}")
                    print(f"   - Categories count: {exp.get('categories_count', 'N/A')}")

                # Verificar flujo diario
                if "daily_flow_chart" in data:
                    flow = data["daily_flow_chart"]
                    print(f"\n📈 FLUJO DIARIO:")
                    print(f"   - Fechas: {len(flow['dates'])} días")
                    print(f"   - Series disponibles: {list(flow['series'].keys())}")

        else:
            print("❌ ERROR EN ANALYTICS")

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
    test_analytics_only_income()
