#!/usr/bin/env python3
"""Script para verificar cobertura de la Fase 1"""

import json
import os

if os.path.exists("coverage.json"):
    with open("coverage.json", encoding="utf-8") as f:
        data = json.load(f)

    # Archivos de la Fase 1 (probar con diferentes formatos de path)
    files_to_check = {
        "accounts/views.py": ["accounts/views.py", "accounts\\views.py"],
        "categories/views.py": ["categories/views.py", "categories\\views.py"],
        "dashboard/services.py": ["dashboard/services.py", "dashboard\\services.py"],
        "utils/views.py": ["utils/views.py", "utils\\views.py"],
    }

    print("=" * 80)
    print("COBERTURA DE LA FASE 1")
    print("=" * 80)

    total_covered = 0
    total_statements = 0

    for name, paths in files_to_check.items():
        file_data = None
        for path in paths:
            if path in data["files"]:
                file_data = data["files"][path]
                break

        if file_data is None:
            # Buscar por nombre de archivo
            for key in data["files"]:
                if key.endswith((name.replace("/", "\\"), name)):
                    file_data = data["files"][key]
                    break

        if file_data:
            summary = file_data.get("summary", {})
            covered = summary.get("covered_lines", 0)
            statements = summary.get("num_statements", 0)
            percent = summary.get("percent_covered", 0)

            total_covered += covered
            total_statements += statements

            print(f"{name:<30} {percent:>6.1f}% ({covered:>4}/{statements:<4} lineas)")
        else:
            print(f"{name:<30} No encontrado en coverage.json")

    print("-" * 80)
    phase1_percent = (total_covered / total_statements * 100) if total_statements > 0 else 0
    print(
        f"{'TOTAL FASE 1':<30} {phase1_percent:>6.1f}% ({total_covered:>4}/{total_statements:<4} líneas)"
    )

    # Cobertura total del proyecto
    totals = data.get("totals", {})
    total_percent = totals.get("percent_covered", 0)
    total_covered_all = totals.get("covered_lines", 0)
    total_statements_all = totals.get("num_statements", 0)

    print("=" * 80)
    print(
        f"{'COBERTURA TOTAL DEL PROYECTO':<30} {total_percent:>6.2f}% ({total_covered_all:>5}/{total_statements_all:<5} líneas)"
    )
    print("=" * 80)

    # Comparación con objetivo
    objetivo = 45.0
    diferencia = total_percent - objetivo
    print(f"\nObjetivo: {objetivo}%")
    print(f"Actual: {total_percent:.2f}%")
    if diferencia >= 0:
        print(f"[OK] Excede el objetivo por {diferencia:.2f}%")
    else:
        print(f"[!] Falta {abs(diferencia):.2f}% para alcanzar el objetivo")
else:
    print(
        "❌ coverage.json no encontrado. Ejecuta primero: python -m pytest tests/ --cov --cov-report=json"
    )
