## Estado DevOps y linters de seguridad (pre-commit)

### ¿Qué se implementó?
- Configuración de **pre-commit** con los hooks:
  - `trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-json`, `check-toml`, `detect-private-key`, `mixed-line-ending`.
  - Formato y lint: `black` (línea 100), `ruff`, `ruff-format`.
  - Seguridad (SAST): `bandit` con severidad baja (`-ll`) y omitiendo reglas `B101` y `B601`.
- Optimización de `bandit`:
  - Escanea solo los archivos Python en stage (sin `-r .`), por lo que es mucho más rápido al commitear.
  - Exclusiones en el hook: `venv/`, `migrations/`, `tests/`, `*test_*.py`, `coverage/`, `htmlcov/` para evitar falsos positivos en dependencias y binarios.
- Limpieza de configuraciones antiguas:
  - Se eliminó `.bandit` que listaba reglas inexistentes y rompía el hook.
  - Toda la configuración vive ahora en `.pre-commit-config.yaml`.

### Cómo ejecutarlo
- Instalación de hooks (una sola vez): `pre-commit install`
- Ejecutar sobre todos los archivos: `pre-commit run --all-files`
- En cada commit los hooks corren automáticamente sobre los archivos modificados.

### Alineación con los requerimientos del proyecto (DevSecOps / CI-CD)
- **Políticas y estándares (Sección 5, DevOps):**
  - Estilo de código y linters: `black`, `ruff`.
  - Seguridad estática (SAST): `bandit` activo en cada commit/PR.
  - Convenciones de ramas y commits: se fomenta Conventional Commits al integrar con pre-commit.
- **Pruebas y calidad continua:**
  - Los hooks bloquean commits con problemas de estilo, formato o seguridad antes de llegar a CI.
  - El escaneo rápido en local complementa un posible escaneo completo en CI (recomendado agregar job de `bandit -r .` en el pipeline).
- **Seguridad mínima:**
  - Análisis de seguridad automático en cada commit (bandit).
  - Prevención de llaves privadas y archivos mal formados en el repo.

### Próximos pasos sugeridos
- Añadir en CI un job dedicado a `bandit -r .` para escanear todo el repo en cada push/PR.
- Publicar badges de estado de CI/CD en el `README.md`.
- Documentar en Confluence/Notion el flujo de ramas y la política de releases (SemVer) y dependencias.
