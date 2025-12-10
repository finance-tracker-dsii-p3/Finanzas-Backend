# Recomendaciones para Aumentar Cobertura de Tests

## Resumen Ejecutivo

**Cobertura actual:** 38.15%
**Cobertura objetivo:** 45%
**Diferencia:** 6.85% (aproximadamente 860 líneas adicionales)

## Estrategia: Enfoque en Alto Impacto y Baja Complejidad

### Top 10 Archivos con Mayor Impacto Potencial

| Archivo | Líneas sin cubrir | Cobertura actual | Prioridad | Dificultad |
|---------|-------------------|-----------------|-----------|------------|
| `transactions/serializers.py` | 326 | 25.9% | 🔴 ALTA | Media |
| `users/views.py` | 200 | 31.0% | 🔴 ALTA | Baja |
| `accounts/views.py` | 129 | 20.9% | 🔴 ALTA | Baja |
| `categories/views.py` | 125 | 20.4% | 🔴 ALTA | Baja |
| `notifications/views.py` | 116 | 23.7% | 🟡 MEDIA | Baja |
| `users/serializers.py` | 102 | 42.0% | 🟡 MEDIA | Media |
| `categories/services.py` | 99 | 22.0% | 🟡 MEDIA | Media |
| `utils/views.py` | 92 | 25.2% | 🟡 MEDIA | Baja |
| `dashboard/services.py` | 62 | 24.0% | 🟢 BAJA | Baja |
| `accounts/serializers.py` | 73 | 42.5% | 🟢 BAJA | Media |

## Plan de Acción Recomendado (Por Orden de Prioridad)

### FASE 1: Views con Baja Complejidad (Impacto: ~450 líneas, ~3.5% cobertura)

#### 1.1 `accounts/views.py` (129 líneas sin cubrir)
**Endpoints a testear:**
- ✅ `summary()` - GET `/api/accounts/summary/` - Resumen financiero
- ✅ `by_currency()` - GET `/api/accounts/by_currency/?currency=COP` - Filtrar por moneda
- ✅ `update_balance()` - POST `/api/accounts/{id}/update_balance/` - Actualizar saldo
- ✅ `toggle_active()` - POST `/api/accounts/{id}/toggle_active/` - Activar/desactivar
- ✅ `list()` - GET `/api/accounts/` - Listar con filtros
- ✅ `create()` - POST `/api/accounts/` - Crear cuenta
- ✅ `update()` - PUT/PATCH `/api/accounts/{id}/` - Actualizar cuenta
- ✅ `destroy()` - DELETE `/api/accounts/{id}/` - Eliminar cuenta

**Tests sugeridos:**
```python
# tests/test_accounts_views.py
- test_account_summary_endpoint
- test_account_by_currency_filter
- test_update_balance_success
- test_update_balance_invalid_amount
- test_toggle_active_account
- test_list_accounts_with_filters
- test_create_account_success
- test_update_account_success
- test_delete_account_success
```

**Impacto estimado:** +129 líneas cubiertas, +1.0% cobertura

---

#### 1.2 `categories/views.py` (125 líneas sin cubrir)
**Endpoints a testear:**
- ✅ `list()` - GET `/api/categories/` - Listar con filtros
- ✅ `delete_with_reassignment()` - POST `/api/categories/{id}/delete_with_reassignment/` - Eliminar con reasignación
- ✅ `stats()` - GET `/api/categories/{id}/stats/` - Estadísticas de categoría
- ✅ `create_defaults()` - POST `/api/categories/create_defaults/` - Crear categorías por defecto
- ✅ `bulk_update_order()` - POST `/api/categories/bulk_update_order/` - Actualizar orden
- ✅ `create()` - POST `/api/categories/` - Crear categoría
- ✅ `update()` - PUT/PATCH `/api/categories/{id}/` - Actualizar categoría
- ✅ `destroy()` - DELETE `/api/categories/{id}/` - Eliminar categoría

**Tests sugeridos:**
```python
# tests/test_categories_views.py
- test_list_categories_with_filters
- test_delete_with_reassignment_success
- test_category_stats_endpoint
- test_create_defaults_categories
- test_bulk_update_order
- test_create_category_success
- test_update_category_success
- test_delete_category_success
```

**Impacto estimado:** +125 líneas cubiertas, +1.0% cobertura

---

#### 1.3 `dashboard/services.py` (62 líneas sin cubrir)
**Métodos a testear:**
- ✅ `get_admin_dashboard_data()` - Dashboard para administradores
- ✅ `get_user_dashboard_data()` - Dashboard para usuarios
- ✅ `_get_recent_activities()` - Actividades recientes del sistema
- ✅ `_get_user_recent_activities()` - Actividades del usuario
- ✅ `_get_alerts()` - Alertas del sistema
- ✅ `_get_user_alerts()` - Alertas del usuario
- ✅ `_get_error_dashboard()` - Dashboard de error

**Tests sugeridos:**
```python
# tests/test_dashboard_services.py
- test_get_admin_dashboard_data
- test_get_user_dashboard_data
- test_get_recent_activities
- test_get_user_recent_activities
- test_get_alerts_with_pending_users
- test_get_user_alerts_verification_pending
- test_get_user_alerts_profile_incomplete
- test_get_error_dashboard
```

**Impacto estimado:** +62 líneas cubiertas, +0.5% cobertura

---

#### 1.4 `utils/views.py` (92 líneas sin cubrir)
**Endpoints a testear:**
- ✅ Listar tipos de cambio
- ✅ Crear/actualizar tipo de cambio
- ✅ Convertir moneda
- ✅ Obtener moneda base

**Impacto estimado:** +92 líneas cubiertas, +0.7% cobertura

---

### FASE 2: Serializers (Impacto: ~200 líneas, ~1.6% cobertura)

#### 2.1 `transactions/serializers.py` (326 líneas sin cubrir)
**⚠️ NOTA:** Este es el archivo con mayor impacto, pero también el más complejo.

**Enfoque recomendado:**
- Testear métodos de validación principales
- Testear conversión de monedas
- Testear serialización de campos calculados
- **Priorizar:** Métodos `validate_*` y `get_*` (SerializersMethodField)

**Tests sugeridos:**
```python
# tests/test_transactions_serializers.py
- test_transaction_serializer_validate_amounts
- test_transaction_serializer_currency_conversion
- test_transaction_serializer_base_currency_fields
- test_transaction_serializer_with_category
- test_transaction_serializer_with_goal
- test_transaction_serializer_with_rule
```

**Impacto estimado:** +150 líneas cubiertas (parcial), +1.2% cobertura

---

#### 2.2 `users/serializers.py` (102 líneas sin cubrir)
**Tests sugeridos:**
```python
# tests/test_users_serializers.py
- test_user_registration_serializer
- test_user_profile_serializer
- test_password_change_serializer
```

**Impacto estimado:** +50 líneas cubiertas, +0.4% cobertura

---

### FASE 3: Services (Impacto: ~99 líneas, ~0.8% cobertura)

#### 3.1 `categories/services.py` (99 líneas sin cubrir)
**Métodos a testear:**
- ✅ `validate_category_deletion()`
- ✅ `delete_category()`
- ✅ `reassign_transactions()`
- ✅ `get_category_stats()`

**Impacto estimado:** +99 líneas cubiertas, +0.8% cobertura

---

## Resumen de Impacto Estimado

| Fase | Archivos | Líneas cubiertas | % Cobertura ganada |
|------|----------|-----------------|-------------------|
| Fase 1 (Views) | 4 archivos | ~408 líneas | ~3.2% |
| Fase 2 (Serializers) | 2 archivos | ~200 líneas | ~1.6% |
| Fase 3 (Services) | 1 archivo | ~99 líneas | ~0.8% |
| **TOTAL** | **7 archivos** | **~707 líneas** | **~5.6%** |

**Cobertura proyectada:** 38.15% + 5.6% = **43.75%** (cerca del objetivo de 45%)

## Recomendaciones Adicionales

### Archivos a Excluir de Cobertura (No críticos)
- `export/management/commands/*` - Scripts de datos de prueba
- `*tests.py` - Archivos de tests (no deberían contar)
- `dashboard/views_clean.py` - Archivo de respaldo
- `finanzas_back/settings.py` - Configuración (ya tiene 0% pero no es crítico)

### Mejores Prácticas
1. **Empezar con Views:** Son más fáciles de testear y tienen alto impacto
2. **Usar APIClient de Django:** Más rápido que requests
3. **Testear casos felices y errores:** Validaciones, casos límite
4. **Mockear servicios externos:** Evitar dependencias reales
5. **Tests unitarios para Services:** Más rápidos que tests de integración

### Orden de Implementación Sugerido
1. ✅ `accounts/views.py` (1-2 horas)
2. ✅ `categories/views.py` (1-2 horas)
3. ✅ `dashboard/services.py` (1 hora)
4. ✅ `utils/views.py` (1 hora)
5. ✅ `categories/services.py` (1-2 horas)
6. ⚠️ `transactions/serializers.py` (3-4 horas - más complejo)
7. ✅ `users/serializers.py` (1 hora)

**Tiempo total estimado:** 10-13 horas de desarrollo

## Comandos Útiles

```bash
# Ejecutar tests con cobertura
python -m pytest tests/ --cov --cov-report=term-missing

# Ver cobertura de un archivo específico
python -m pytest tests/test_accounts_views.py --cov=accounts.views --cov-report=term-missing

# Generar reporte HTML
python -m pytest tests/ --cov --cov-report=html
# Abrir: htmlcov/index.html
```
