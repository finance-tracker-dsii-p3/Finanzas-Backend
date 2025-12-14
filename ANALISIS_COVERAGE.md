# Análisis de Coverage para Alcanzar 55%

## Estado Actual
- **Coverage actual:** 53.99%
- **Coverage objetivo:** 55.00%
- **Diferencia:** 1.01%
- **Líneas necesarias:** ~153 líneas adicionales cubiertas

## Áreas Prioritarias para Aumentar Coverage

### 1. **transactions/serializers.py** (30.7% coverage - 282 líneas faltantes)
**Potencial:** ⭐⭐⭐⭐⭐ (Muy Alto)
**Líneas disponibles:** 282 líneas sin cubrir

**Métodos principales sin cubrir:**
- `TransactionSerializer.validate()` - Validaciones complejas de montos (líneas 213-636)
- `TransactionSerializer.create()` - Creación de transacciones (línea 636)
- `TransactionUpdateSerializer.validate()` - Validaciones de actualización (líneas 708-749)
- `TransactionDetailSerializer.get_base_equivalent_amount()` - Conversión de monedas
- `TransactionDetailSerializer.get_base_exchange_rate()` - Tasas de cambio
- `TransactionDetailSerializer.get_base_exchange_rate_warning()` - Advertencias

**Recomendación:** Agregar tests para validaciones de montos (base_amount, total_amount, tax_percentage) y métodos de conversión de moneda. Esto podría cubrir ~100-150 líneas fácilmente.

---

### 2. **export/services.py** (0.0% coverage - 126 líneas faltantes)
**Potencial:** ⭐⭐⭐⭐ (Alto)
**Líneas disponibles:** 126 líneas sin cubrir

**Métodos principales:**
- `BasicDataExporter.__init__()` - Inicialización
- `BasicDataExporter.export_users_data()` - Exportar usuarios
- `BasicDataExporter.export_notifications_data()` - Exportar notificaciones
- `process_export_job()` - Procesar trabajo de exportación

**Recomendación:** Agregar tests básicos para exportación de datos. Esto podría cubrir ~50-80 líneas.

---

### 3. **vehicles/serializers.py** (35.9% coverage - 73 líneas faltantes)
**Potencial:** ⭐⭐⭐ (Medio-Alto)
**Líneas disponibles:** 73 líneas sin cubrir

**Métodos principales:**
- `VehicleSerializer.validate_plate()` - Validación de placa única
- `SOATSerializer` - Serialización de SOAT
- `SOATAlertSerializer` - Serialización de alertas

**Recomendación:** Agregar tests para validaciones de placa y serialización de SOAT. Esto podría cubrir ~40-60 líneas.

---

### 4. **vehicles/services.py** (13.0% coverage - 77 líneas faltantes)
**Potencial:** ⭐⭐⭐ (Medio)
**Líneas disponibles:** 77 líneas sin cubrir

**Métodos principales:**
- `register_payment()` - Registrar pago de SOAT
- `check_and_create_alerts()` - Verificar y crear alertas
- `get_payment_history()` - Obtener historial de pagos
- `mark_alert_as_read()` - Marcar alerta como leída

**Recomendación:** Agregar tests para servicios de vehículos. Esto podría cubrir ~40-60 líneas.

---

### 5. **dashboard/views_clean.py** (0.0% coverage - 86 líneas faltantes)
**Potencial:** ⭐⭐ (Medio)
**Líneas disponibles:** 86 líneas sin cubrir

**Nota:** Este archivo parece ser una versión "limpia" de views. Verificar si está en uso.

---

## Plan de Acción Recomendado

### Opción 1: Enfoque en transactions/serializers.py (Más Eficiente)
- Agregar tests para `TransactionSerializer.validate()` cubriendo diferentes casos de montos
- Agregar tests para `TransactionUpdateSerializer.validate()`
- Agregar tests para métodos de conversión de moneda en `TransactionDetailSerializer`
- **Estimado:** ~120-150 líneas cubiertas → Coverage: ~55.5-56%

### Opción 2: Combinación de Múltiples Módulos
1. **transactions/serializers.py:** ~80 líneas
2. **export/services.py:** ~50 líneas
3. **vehicles/serializers.py:** ~30 líneas
- **Total:** ~160 líneas → Coverage: ~55.5%

### Opción 3: Enfoque Distribuido
1. **transactions/serializers.py:** ~60 líneas
2. **export/services.py:** ~40 líneas
3. **vehicles/serializers.py:** ~30 líneas
4. **vehicles/services.py:** ~30 líneas
- **Total:** ~160 líneas → Coverage: ~55.5%

## Recomendación Final

**Priorizar `transactions/serializers.py`** porque:
1. Tiene el mayor número de líneas sin cubrir (282)
2. Los métodos son relativamente fáciles de testear (validaciones)
3. Un solo archivo puede aportar suficientes líneas para alcanzar el 55%
4. Es código crítico del negocio que debería estar testeado

**Siguiente paso:** Crear tests para `TransactionSerializer.validate()` y `TransactionUpdateSerializer.validate()` cubriendo diferentes casos de entrada (montos como float, string, int, con/sin impuestos, etc.)
