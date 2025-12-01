#!/usr/bin/env python
"""
Script para probar los mismos checks que ejecuta CI/CD
"""

import os
import sys
import subprocess


def run_command(command, description):
    """Ejecutar un comando y mostrar el resultado"""
    print(f"\n[TEST] {description}")
    print(f"   Comando: {command}")
    print("-" * 50)

    try:
        result = subprocess.run(command.split(), capture_output=True, text=True, timeout=60)

        print(f"   Exit code: {result.returncode}")

        if result.stdout:
            print("   STDOUT:")
            for line in result.stdout.strip().split("\n"):
                print(f"     {line}")

        if result.stderr:
            print("   STDERR:")
            for line in result.stderr.strip().split("\n"):
                print(f"     {line}")

        if result.returncode == 0:
            print("   [OK] EXITO")
            return True
        else:
            print("   [ERROR] FALLO")
            return False

    except subprocess.TimeoutExpired:
        print("   [ERROR] TIMEOUT (60 segundos)")
        return False
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False


def main():
    """Ejecutar todos los checks de CI/CD"""
    print("[CI/CD] Probando checks de CI/CD")
    print("=" * 50)

    checks = [
        ("python manage.py check", "Django System Check"),
        ("python manage.py makemigrations --check --dry-run", "Migration Check"),
        ("python manage.py test --verbosity 1 --keepdb", "Test Suite"),
    ]

    results = []

    for command, description in checks:
        success = run_command(command, description)
        results.append((description, success))

    # Resumen
    print("\n[RESUMEN] Resumen de Checks:")
    print("=" * 50)

    success_count = 0
    for description, success in results:
        status = "[OK] EXITO" if success else "[ERROR] FALLO"
        print(f"   - {description}: {status}")
        if success:
            success_count += 1

    print(f"\n[RESULTADO] {success_count}/{len(results)} checks exitosos")

    if success_count == len(results):
        print("[OK] Todos los checks pasaron!")
        print("   El proyecto esta listo para CI/CD")
    else:
        print("[WARNING] Algunos checks fallaron")
        print("   Revisa los errores antes de hacer push")

    return success_count == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
