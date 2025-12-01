"""
Script para obtener token de autenticación para testing
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "finanzas_back.settings")
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()


def get_test_token():
    """Obtener token para testing"""

    # Obtener usuario de prueba
    user = User.objects.filter(username="usuarioPrueba").first()
    if not user:
        print("❌ Usuario 'usuarioPrueba' no encontrado")
        return

    # Obtener o crear token
    token, created = Token.objects.get_or_create(user=user)

    print("🔑 TOKEN PARA TESTING:")
    print(f"Usuario: {user.username}")
    print(f"Token: {token.key}")
    print(f"{'✅ Creado' if created else '🔄 Existente'}")

    print("\n📋 USAR EN POSTMAN:")
    print(f"Authorization: Token {token.key}")

    print("\n🧪 CURL DE PRUEBA:")
    print(
        f'curl -H "Authorization: Token {token.key}" http://localhost:8000/api/analytics/dashboard/'
    )


if __name__ == "__main__":
    get_test_token()
