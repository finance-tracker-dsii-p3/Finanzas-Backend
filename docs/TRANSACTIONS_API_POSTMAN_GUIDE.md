# 💰 API de Transacciones Financieras - Guía de Postman

Esta guía te ayudará a probar todos los endpoints de la API de **Transacciones Financieras** usando Postman.

---

## 🔐 Configuración Inicial

### 1. Variables de Entorno en Postman

Crea una colección en Postman y configura estas variables:

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `base_url` | `http://localhost:8000` | URL base del backend |
| `token` | `Token xxxxx...` | Token de autenticación del usuario |

### 2. Autenticación

Todos los endpoints requieren autenticación. En cada petición, agrega el header:

```
Authorization: {{token}}
```

---

## 💰 Endpoints de Transacciones

### 1. Listar Todas las Transacciones

**Método:** `GET`
**URL:** `{{base_url}}/api/transactions/`

**Headers:**
```
Authorization: {{token}}
```

**Query Parameters (Opcionales):**
- `type=1` - Filtrar por tipo (1=Ingreso, 2=Gasto, 3=Transferencia, 4=Ahorro)
- `category={id}` - Filtrar por categoría
- `applied_rule={id}` - Filtrar por regla aplicada
- `date_from=2025-11-01` - Desde fecha
- `date_to=2025-11-30` - Hasta fecha
- `min_amount=1000` - Monto mínimo
- `max_amount=50000` - Monto máximo
- `search=texto` - Buscar en descripción
- `ordering=date,-total_amount` - Ordenar por campos

**Ejemplo básico:**
```
GET {{base_url}}/api/transactions/
```

**Ejemplo con filtros:**
```
GET {{base_url}}/api/transactions/?type=2&date_from=2025-11-01&ordering=-date
```

**Respuesta Exitosa (200 OK):**
```json
{
  "count": 5,
  "message": "5 transacciones encontradas",
  "results": [
    {
      "id": 1,
      "user": 12,
      "origin_account": 1,
      "destination_account": null,
      "type": 2,
      "base_amount": 45000,
      "tax_percentage": null,
      "taxed_amount": 0,
      "total_amount": 45000,
      "date": "2025-11-23",
      "tag": "comida",
      "description": "Almuerzo restaurante italiano",
      "category": 17,
      "applied_rule": null,
      "created_at": "2025-11-24T01:27:31.716382Z",
      "updated_at": "2025-11-24T01:27:31.716406Z"
    }
  ]
}
```

**Respuesta sin datos:**
```json
{
  "count": 0,
  "message": "No tienes transacciones creadas.",
  "results": []
}
```

---

### 2. Crear Nueva Transacción

**Método:** `POST`
**URL:** `{{base_url}}/api/transactions/`

**Headers:**
```
Authorization: {{token}}
Content-Type: application/json
```

**Body (JSON):**

#### Transacción de Ingreso:
```json
{
  "origin_account": 3,
  "type": 1,
  "base_amount": 2500000,
  "date": "2025-11-24",
  "description": "Salario mensual",
  "tag": "salario"
}
```

⚠️ **IMPORTANTE:** Usa un ID de cuenta válido. Para verificar tus cuentas disponibles:
```
GET {{base_url}}/api/accounts/
```

#### Transacción de Gasto:
```json
{
  "origin_account": 1,
  "type": 2,
  "base_amount": 45000,
  "tax_percentage": 10,
  "date": "2025-11-24",
  "description": "Almuerzo restaurante",
  "tag": "comida",
  "category": 17
}
```

#### Transacción de Transferencia:
```json
{
  "origin_account": 1,
  "destination_account": 2,
  "type": 3,
  "base_amount": 100000,
  "date": "2025-11-24",
  "description": "Transferencia entre cuentas",
  "tag": "transfer"
}
```

#### Transacción de Ahorro:
```json
{
  "origin_account": 1,
  "type": 4,
  "base_amount": 200000,
  "date": "2025-11-24",
  "description": "Ahorro mensual",
  "tag": "ahorro"
}
```

**Campos Obligatorios:**
- `origin_account` - ID de la cuenta de origen (debe existir y pertenecer al usuario)
- `type` - Tipo de transacción (1-4)
- `base_amount` - Monto base (número positivo)
- `date` - Fecha en formato YYYY-MM-DD

**Campos Opcionales:**
- `destination_account` - Solo para transferencias (type=3)
- `tax_percentage` - Porcentaje de impuesto (se calcula automáticamente `taxed_amount` y `total_amount`)
- `description` - Descripción del movimiento (activa reglas automáticas)
- `tag` - Etiqueta personalizada
- `category` - ID de categoría (o se asigna automáticamente por reglas)

**Campos Calculados Automáticamente:**
- `taxed_amount` - Monto del impuesto
- `total_amount` - Monto total (base + impuestos)
- `applied_rule` - Regla automática aplicada (si aplica)
- `created_at` / `updated_at` - Timestamps

**Respuesta Exitosa (201 Created):**
```json
{
  "id": 15,
  "user": 12,
  "origin_account": 1,
  "destination_account": null,
  "type": 2,
  "base_amount": 45000,
  "tax_percentage": 10,
  "taxed_amount": 4500,
  "total_amount": 49500,
  "date": "2025-11-24",
  "tag": "comida",
  "description": "Almuerzo restaurante",
  "category": 17,
  "applied_rule": null,
  "created_at": "2025-11-24T15:30:00.000Z",
  "updated_at": "2025-11-24T15:30:00.000Z"
}
```

---

### 3. Ver Detalle de Transacción

**Método:** `GET`
**URL:** `{{base_url}}/api/transactions/{id}/`

**Headers:**
```
Authorization: {{token}}
```

**Ejemplo:**
```
GET {{base_url}}/api/transactions/1/
```

**Respuesta Exitosa (200 OK):**
```json
{
  "id": 1,
  "user": 12,
  "origin_account": 1,
  "destination_account": null,
  "type": 2,
  "base_amount": 45000,
  "tax_percentage": 10,
  "taxed_amount": 4500,
  "total_amount": 49500,
  "date": "2025-11-24",
  "tag": "comida",
  "description": "Almuerzo restaurante italiano",
  "category": 17,
  "applied_rule": null,
  "created_at": "2025-11-24T01:27:31.716382Z",
  "updated_at": "2025-11-24T01:27:31.716406Z"
}
```

---

### 4. Actualizar Transacción Completa

**Método:** `PUT`
**URL:** `{{base_url}}/api/transactions/{id}/`

**Headers:**
```
Authorization: {{token}}
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "origin_account": 1,
  "type": 2,
  "base_amount": 50000,
  "tax_percentage": 15,
  "date": "2025-11-24",
  "description": "Cena restaurante actualizada",
  "tag": "cena"
}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "id": 1,
  "user": 12,
  "origin_account": 1,
  "destination_account": null,
  "type": 2,
  "base_amount": 50000,
  "tax_percentage": 15,
  "taxed_amount": 7500,
  "total_amount": 57500,
  "date": "2025-11-24",
  "tag": "cena",
  "description": "Cena restaurante actualizada"
}
```

---

### 5. Actualizar Transacción Parcial

**Método:** `PATCH`
**URL:** `{{base_url}}/api/transactions/{id}/`

**Headers:**
```
Authorization: {{token}}
Content-Type: application/json
```

**Body (JSON) - Solo los campos a actualizar:**
```json
{
  "description": "Nueva descripción",
  "tag": "nuevo_tag"
}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "id": 1,
  "user": 12,
  "origin_account": 1,
  "destination_account": null,
  "type": 2,
  "base_amount": 50000,
  "tax_percentage": 15,
  "taxed_amount": 7500,
  "total_amount": 57500,
  "date": "2025-11-24",
  "tag": "nuevo_tag",
  "description": "Nueva descripción"
}
```

---

### 6. Eliminar Transacción

**Método:** `DELETE`
**URL:** `{{base_url}}/api/transactions/{id}/`

**Headers:**
```
Authorization: {{token}}
```

**Ejemplo:**
```
DELETE {{base_url}}/api/transactions/1/
```

**Respuesta Exitosa (204 No Content):**
```
(Sin contenido - solo status 204)
```

---

## 📊 Tipos de Transacciones

| Tipo | Valor | Descripción | Campos Requeridos |
|------|-------|-------------|-------------------|
| Income | 1 | Ingresos | `origin_account`, `base_amount` |
| Expense | 2 | Gastos | `origin_account`, `base_amount` |
| Transfer | 3 | Transferencias | `origin_account`, `destination_account`, `base_amount` |
| Saving | 4 | Ahorros | `origin_account`, `base_amount` |

---

## 🔍 Filtros Disponibles

### Por Tipo de Transacción
```
GET {{base_url}}/api/transactions/?type=2
```

### Por Rango de Fechas
```
GET {{base_url}}/api/transactions/?date_from=2025-11-01&date_to=2025-11-30
```

### Por Monto
```
GET {{base_url}}/api/transactions/?min_amount=10000&max_amount=100000
```

### Por Categoría
```
GET {{base_url}}/api/transactions/?category=17
```

### Búsqueda en Descripción
```
GET {{base_url}}/api/transactions/?search=restaurante
```

### Ordenamiento
```
GET {{base_url}}/api/transactions/?ordering=-date,total_amount
```

### Filtros Combinados
```
GET {{base_url}}/api/transactions/?type=2&date_from=2025-11-01&search=comida&ordering=-date
```

---

## 💡 Casos de Uso Completos

### Caso 1: Crear Gasto con Impuestos y Categoría

**Paso 1: Obtener categorías disponibles**
```
GET {{base_url}}/api/categories/?type=expense
```

**Paso 2: Crear gasto**
```json
{
  "origin_account": 1,
  "type": 2,
  "base_amount": 85000,
  "tax_percentage": 19,
  "date": "2025-11-24",
  "description": "Compra supermercado semanal",
  "tag": "mercado",
  "category": 17
}
```

---

### Caso 2: Transferencia Entre Cuentas

**Paso 1: Listar cuentas disponibles**
```
GET {{base_url}}/api/accounts/
```

**Paso 2: Crear transferencia**
```json
{
  "origin_account": 1,
  "destination_account": 2,
  "type": 3,
  "base_amount": 500000,
  "date": "2025-11-24",
  "description": "Transferencia a cuenta de ahorros",
  "tag": "transfer"
}
```

---

### Caso 3: Registro de Ingresos Mensuales

**Crear ingreso por salario:**
```json
{
  "origin_account": 1,
  "type": 1,
  "base_amount": 3000000,
  "date": "2025-11-30",
  "description": "Salario noviembre 2025",
  "tag": "salario"
}
```

---

### Caso 4: Análisis de Gastos del Mes

**Paso 1: Obtener gastos del mes actual**
```
GET {{base_url}}/api/transactions/?type=2&date_from=2025-11-01&date_to=2025-11-30&ordering=-date
```

**Paso 2: Filtrar por categoría específica**
```
GET {{base_url}}/api/transactions/?type=2&category=17&date_from=2025-11-01
```

---

## ❌ Errores Comunes y Soluciones

### Error 400 - Datos inválidos
**Causa:** Datos requeridos faltantes o formato incorrecto
**Ejemplo de respuesta:**
```json
{
  "base_amount": ["Este campo es requerido."],
  "date": ["Formato de fecha inválido. Use YYYY-MM-DD."]
}
```
**Solución:** Verificar que todos los campos obligatorios estén presentes y con formato correcto

### Error 401 - No autenticado
**Causa:** Token no válido o no enviado
**Solución:** Verificar header `Authorization: Token xxxxx`

### Error 404 - Transacción no encontrada
**Causa:** ID de transacción no existe o no pertenece al usuario
**Solución:** Verificar que el ID sea correcto y que la transacción pertenezca al usuario autenticado

### Error 400 - Cuenta inexistente
**Causa:** ID de cuenta no válido o no pertenece al usuario
**Ejemplo:**
```json
{
  "origin_account": ["Clave primaria \"1\" inválida - objeto no existe."]
}
```
**Solución:** Verificar cuentas disponibles con `GET /api/accounts/` y usar un ID válido

### Error 400 - Campo requerido faltante
**Causa:** Campos calculados incluidos como requeridos
**Ejemplo:**
```json
{
  "total_amount": ["Este campo es requerido."]
}
```
**Solución:** NO incluir `total_amount`, `taxed_amount` en la petición - se calculan automáticamente

### Error 400 - Validación de transferencia
**Causa:** Transferencia sin cuenta destino
**Ejemplo:**
```json
{
  "destination_account": ["La cuenta destino es obligatoria para transferencias."]
}
```
**Solución:** Para tipo=3 (transferencia), incluir `destination_account`

---

## 🧪 Casos de Prueba Específicos

### Prueba 1: Crear transacción con reglas automáticas
```json
{
  "origin_account": 1,
  "type": 2,
  "base_amount": 25000,
  "date": "2025-11-24",
  "description": "Uber aeropuerto"
}
```
**Resultado esperado:** Si hay reglas configuradas para "Uber", se asignará categoría automáticamente

### Prueba 2: Validación de montos negativos
```json
{
  "origin_account": 1,
  "type": 2,
  "base_amount": -1000,
  "date": "2025-11-24"
}
```
**Resultado esperado:** Error 400 - "El monto debe ser un valor positivo mayor que cero."

### Prueba 3: Cálculo automático de impuestos
```json
{
  "origin_account": 1,
  "type": 2,
  "base_amount": 100000,
  "tax_percentage": 19,
  "date": "2025-11-24"
}
```
**Resultado esperado:**
- `taxed_amount`: 19000
- `total_amount`: 119000

### Prueba 4: Sin datos (usuario nuevo)
```
GET {{base_url}}/api/transactions/
```
**Resultado esperado:**
```json
{
  "count": 0,
  "message": "No tienes transacciones creadas.",
  "results": []
}
```

---

## 🚀 Colección de Postman para Transacciones

```
📁 Finanzas Backend - Transacciones
  📁 CRUD Básico
    ├─ GET Listar Todas las Transacciones
    ├─ POST Crear Ingreso
    ├─ POST Crear Gasto
    ├─ POST Crear Transferencia
    ├─ POST Crear Ahorro
    ├─ GET Ver Detalle
    ├─ PUT Actualizar Completa
    ├─ PATCH Actualizar Parcial
    └─ DELETE Eliminar
  📁 Filtros y Búsquedas
    ├─ GET Filtrar por Tipo
    ├─ GET Filtrar por Fechas
    ├─ GET Filtrar por Monto
    ├─ GET Filtrar por Categoría
    ├─ GET Buscar en Descripción
    └─ GET Ordenamiento
  📁 Casos de Uso Reales
    ├─ POST Gasto con Impuestos
    ├─ POST Transferencia Entre Cuentas
    ├─ GET Gastos del Mes
    ├─ GET Ingresos del Año
    └─ POST Transacción con Regla Automática
  📁 Validaciones
    ├─ POST Error - Monto Negativo
    ├─ POST Error - Transferencia Sin Destino
    ├─ POST Error - Datos Faltantes
    └─ GET Error - ID No Existe
```

---

## 🔗 Integración con Otros Módulos

### Con Analytics
- Las transacciones se utilizan automáticamente en `GET /api/analytics/dashboard/`
- Filtros por período y categoría para análisis financiero

### Con Categorías
- Asignar categoría: `"category": {id}`
- Ver categorías: `GET /api/categories/`

### Con Cuentas
- Cuenta origen obligatoria: `"origin_account": {id}`
- Ver cuentas: `GET /api/accounts/`

### Con Reglas Automáticas
- Las reglas se aplican automáticamente al crear transacciones
- Ver reglas: `GET /api/rules/`

---

**¡Happy Transaction Testing! 💰📊**
