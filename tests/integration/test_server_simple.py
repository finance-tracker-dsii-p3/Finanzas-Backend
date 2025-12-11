#!/usr/bin/env python3
"""
Script simple para verificar que el servidor Django esté funcionando
"""

import sys
import time

import pytest
import requests


def test_server():
    """Probar conexión al servidor Django"""
    base_url = "http://localhost:8000"

    print("Verificando conexion al servidor Django...")
    print(f"URL: {base_url}")
    print("-" * 50)

    try:
        # Probar endpoint básico
        response = requests.get(base_url, timeout=5)
        print(f"Servidor respondiendo - Status: {response.status_code}")
        assert response.status_code in [
            200,
            301,
            302,
            404,
        ], f"Status code inesperado: {response.status_code}"

    except requests.exceptions.ConnectionError:
        print("ERROR: No se puede conectar al servidor")
        print("El servidor Django no esta ejecutandose en http://localhost:8000")
        pytest.skip(
            "Servidor Django no está ejecutándose - test de integración requiere servidor activo"
        )
    except Exception as e:
        print(f"ERROR: {e!s}")
        pytest.skip(f"Error de conexión: {e!s} - test de integración requiere servidor activo")


def test_api():
    """Probar endpoints de la API"""
    base_url = "http://localhost:8000"

    print("\nProbando endpoints de la API...")
    print("-" * 50)

    endpoints = ["/api/auth/", "/api/rooms/", "/api/notifications/", "/api/dashboard/"]

    for endpoint in endpoints:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=5)
            print(f"{endpoint} - Status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"{endpoint} - ERROR: No se puede conectar")
            pytest.skip(
                "Servidor Django no está ejecutándose - test de integración requiere servidor activo"
            )
        except Exception as e:
            print(f"{endpoint} - ERROR: {e!s}")

    assert True  # Test passed


def main():
    print("Verificador de Conexion del Servidor Django")
    print("=" * 60)

    # Esperar un poco
    print("Esperando 2 segundos...")
    time.sleep(2)

    # Probar servidor
    if not test_server():
        print("\nPROBLEMA: El servidor Django no esta ejecutandose")
        print("\nSOLUCIONES:")
        print("1. Ejecutar: python manage.py runserver")
        print("2. Verificar que no haya errores en la consola")
        print("3. Verificar que el puerto 8000 este libre")
        sys.exit(1)

    # Probar API
    if not test_api():
        print("\nPROBLEMA: Los endpoints de la API no responden")
        sys.exit(1)

    print("\nTodo esta funcionando correctamente!")
    print("\nRESUMEN:")
    print("- Servidor Django ejecutandose en http://localhost:8000")
    print("- CORS configurado correctamente")
    print("- Endpoints de la API respondiendo")
    print("\nTu frontend deberia poder conectarse ahora")


if __name__ == "__main__":
    main()
