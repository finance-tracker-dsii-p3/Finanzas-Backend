# HU-21: Implementación de Timezone del Usuario en SOAT

## 📋 Resumen

Se ha implementado el uso del timezone del usuario en todas las operaciones relacionadas con SOAT, cumpliendo con el DoD-02 de la HU-21.

**Fecha de implementación:** 2024-01-XX
**Estado:** ✅ Completo y testeado
**Tests:** 15/15 pasando ✅

---

## ✅ Cambios Implementados

### 1. Modelo SOAT (`vehicles/models.py`)

#### Métodos Modificados:

**`days_until_expiry(user_tz=None)`**
- Ahora acepta un parámetro `user_tz` para usar el timezone del usuario
- Si no se proporciona, intenta obtenerlo de `user.notification_preferences.timezone_object`
- Si no hay preferencias, usa el timezone del servidor

**`is_expired(user_tz=None)`**
- Usa `days_until_expiry` con timezone del usuario
- Verifica si el SOAT está vencido según el timezone del usuario

**`is_near_expiry(user_tz=None)`**
- Usa `days_until_expiry` con timezone del usuario
- Verifica si está próximo a vencer según el timezone del usuario

**`update_status(user_tz=None)`**
- Actualiza el estado del SOAT usando timezone del usuario
- Si no se proporciona, intenta obtenerlo del usuario

**Método auxiliar:**
- `_get_user_timezone()`: Obtiene el timezone del usuario si está disponible

#### Compatibilidad:

Se mantiene compatibilidad con código existente:
- Los métodos pueden llamarse sin parámetros y automáticamente usan el timezone del usuario
- Si el usuario no tiene preferencias, se usa el timezone del servidor

---

### 2. Servicio SOATService (`vehicles/services.py`)

#### Método Modificado:

**`check_and_create_alerts()`**
- Ahora obtiene el timezone de cada usuario antes de procesar sus SOATs
- Usa `select_related` para optimizar consultas: `vehicle__user__notification_preferences`
- Calcula días hasta vencimiento usando el timezone del usuario
- Actualiza el estado usando el timezone del usuario

**Código clave:**
```python
# Obtener timezone del usuario
try:
    prefs = user.notification_preferences
    user_tz = prefs.timezone_object
except Exception:
    # Si no hay preferencias, usar timezone del servidor
    user_tz = None

# Calcular días usando timezone del usuario
days = soat.days_until_expiry(user_tz=user_tz)

# Actualizar estado usando timezone del usuario
soat.update_status(user_tz=user_tz)
```

---

### 3. Serializers (`vehicles/serializers.py`)

#### Serializers Modificados:

**`SOATSerializer`**
- `days_until_expiry`, `is_expired`, `is_near_expiry` ahora son `SerializerMethodField`
- Cada método obtiene el timezone del usuario desde `request.user`
- Usa el timezone del usuario para calcular los valores

**`VehicleWithSOATSerializer`**
- `get_active_soat()` ahora usa el timezone del usuario para filtrar SOATs activos
- Calcula `days_until_expiry` usando el timezone del usuario

---

### 4. Admin (`vehicles/admin.py`)

#### Cambios:

- Se agregaron métodos de display: `days_until_expiry_display`, `is_expired_display`, `is_near_expiry_display`
- Estos métodos llaman a los métodos del modelo que usan timezone del usuario

---

## 🧪 Tests Implementados

### Tests Nuevos (4 tests):

1. **`test_days_until_expiry_with_timezone`**
   - Verifica que el cálculo de días funciona con timezone del usuario
   - Crea preferencias de notificación con timezone específico
   - Verifica que el resultado es correcto

2. **`test_is_expired_with_timezone`**
   - Verifica que `is_expired` funciona con timezone del usuario
   - Crea SOAT vencido y verifica con timezone del usuario

3. **`test_is_near_expiry_with_timezone`**
   - Verifica que `is_near_expiry` funciona con timezone del usuario
   - Crea SOAT próximo a vencer y verifica con timezone del usuario

4. **`test_check_and_create_alerts_with_timezone`**
   - Verifica que el servicio de alertas usa timezone del usuario
   - Crea preferencias con timezone específico
   - Ejecuta el servicio y verifica que funciona correctamente

### Tests Actualizados (3 tests):

1. **`test_days_until_expiry`** - Actualizado para usar método sin parámetros
2. **`test_is_expired`** - Actualizado para usar método sin parámetros
3. **`test_is_near_expiry`** - Actualizado para usar método sin parámetros

---

## ✅ Resultados de Tests

```
Ran 15 tests in 0.196s
OK
```

**Tests pasando:** 15/15 ✅

- ✅ 6 tests de modelos (incluyendo 3 nuevos con timezone)
- ✅ 2 tests de servicios (incluyendo 1 nuevo con timezone)
- ✅ 4 tests de API
- ✅ 3 tests de vehículos

---

## 🔍 Verificación de Funcionamiento

### Escenario 1: Usuario con timezone configurado

```python
# Usuario con timezone "America/New_York"
user = User.objects.get(username="usuario1")
prefs = user.notification_preferences  # timezone="America/New_York"

# SOAT que vence en 10 días
soat = SOAT.objects.get(id=1)

# Calcular días usando timezone del usuario
days = soat.days_until_expiry()  # Usa timezone del usuario automáticamente
# Resultado: 10 días (calculado según timezone de New York)
```

### Escenario 2: Usuario sin timezone configurado

```python
# Usuario sin preferencias de notificación
user = User.objects.get(username="usuario2")
# No tiene notification_preferences

# SOAT que vence en 10 días
soat = SOAT.objects.get(id=2)

# Calcular días (usa timezone del servidor)
days = soat.days_until_expiry()  # Usa timezone del servidor
# Resultado: 10 días (calculado según timezone del servidor)
```

### Escenario 3: Comando cron con múltiples usuarios

```python
# Ejecutar comando cron
python manage.py check_soat_alerts

# El comando:
# 1. Obtiene todos los SOATs con sus usuarios y preferencias
# 2. Para cada SOAT, obtiene el timezone del usuario
# 3. Calcula días y actualiza estado usando el timezone del usuario
# 4. Crea alertas según el timezone del usuario
```

---

## 📊 Impacto en Funcionalidad

### Antes:
- ❌ Todas las fechas se calculaban usando timezone del servidor
- ❌ Alertas podían generarse en momentos incorrectos para usuarios en diferentes zonas horarias
- ❌ El cálculo de días hasta vencimiento podía ser incorrecto

### Después:
- ✅ Las fechas se calculan usando el timezone del usuario
- ✅ Alertas se generan según el timezone del usuario
- ✅ El cálculo de días hasta vencimiento es correcto para cada usuario
- ✅ Compatibilidad mantenida con código existente

---

## 🔧 Configuración Requerida

### Para Usuarios:

Los usuarios deben tener configurado su timezone en `UserNotificationPreferences`:

```python
from users.models import UserNotificationPreferences

prefs = UserNotificationPreferences.objects.create(
    user=user,
    timezone="America/Bogota",  # o cualquier timezone válido
)
```

### Timezones Soportados:

Cualquier timezone válido de pytz:
- `America/Bogota` (Colombia)
- `America/New_York` (USA Este)
- `America/Los_Angeles` (USA Oeste)
- `Europe/Madrid` (España)
- etc.

---

## ✅ Cumplimiento de DoD-02

**DoD-02: Alertas cron programadas con TZ del usuario**

- ✅ **Implementado:** El comando `check_soat_alerts` ahora usa el timezone del usuario
- ✅ **Verificado:** Tests confirman que funciona correctamente
- ✅ **Documentado:** Este documento explica la implementación

**Estado:** ✅ **COMPLETO**

---

## 🚀 Próximos Pasos

1. ✅ Implementación completada
2. ✅ Tests creados y pasando
3. ✅ Documentación actualizada
4. ⏭️ Frontend puede consumir la API (ya funciona con timezone)

---

## 📝 Notas Técnicas

### Compatibilidad:

- El código es retrocompatible: si no hay timezone del usuario, usa el del servidor
- Los métodos pueden llamarse sin parámetros y funcionan automáticamente
- Los serializers obtienen el timezone del usuario desde `request.user`

### Performance:

- Se usa `select_related` para optimizar consultas en `check_and_create_alerts`
- El timezone se obtiene una vez por usuario en el servicio de alertas
- No hay impacto significativo en performance

### Manejo de Errores:

- Si hay error al obtener el timezone del usuario, se usa el del servidor
- Si el timezone es inválido, se usa el del servidor
- Todos los errores se manejan silenciosamente para no interrumpir el flujo

---

## ✅ Conclusión

La implementación del timezone del usuario en SOAT está **100% completa**:

- ✅ Modelo actualizado
- ✅ Servicio actualizado
- ✅ Serializers actualizados
- ✅ Admin actualizado
- ✅ Tests creados y pasando (15/15)
- ✅ Documentación completa

**La HU-21 ahora cumple con todos los criterios de aceptación y Definition of Done.**
