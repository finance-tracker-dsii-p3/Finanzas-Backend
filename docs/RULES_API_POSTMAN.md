# 🤖 API de Reglas Automáticas - Guía de Postman (HU-12)

Esta guía te ayudará a probar todos los endpoints de la API de **Reglas Automáticas** usando Postman.

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

### 3. Obtener Token de Autenticación

**Endpoint:** `POST {{base_url}}/api/auth/login/`

**Body (JSON):**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "tu_password"
}
```

---

## 📋 Endpoints CRUD Básicos

### 1. Listar Reglas Automáticas

**Método:** `GET`  
**URL:** `{{base_url}}/api/rules/`

**Headers:**
```
Authorization: {{token}}
```

**Query Parameters (Opcionales):**
- `active_only=true` - Solo reglas activas
- `criteria_type=description_contains` - Filtrar por criterio de descripción
- `criteria_type=transaction_type` - Filtrar por criterio de tipo de transacción
- `action_type=assign_category` - Filtrar por acción de categoría
- `action_type=assign_tag` - Filtrar por acción de etiqueta
- `search=texto` - Buscar en nombre y palabra clave

**Ejemplo con filtros:**
```
GET {{base_url}}/api/rules/?active_only=true&criteria_type=description_contains
```

**Respuesta Exitosa (200 OK):**
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "name": "Uber y taxis",
      "criteria_type": "description_contains",
      "criteria_type_display": "Descripción contiene texto",
      "keyword": "uber",
      "target_transaction_type": null,
      "target_transaction_type_display": null,
      "action_type": "assign_category",
      "action_type_display": "Asignar categoría",
      "target_category": 5,
      "target_category_name": "Transporte",
      "target_category_color": "#EA580C",
      "target_category_icon": "fa-car",
      "target_tag": null,
      "is_active": true,
      "order": 1,
      "applied_count": 12,
      "created_at": "2025-11-23T10:00:00Z",
      "updated_at": "2025-11-23T14:30:00Z"
    },
    {
      "id": 2,
      "name": "Todos los ingresos",
      "criteria_type": "transaction_type",
      "criteria_type_display": "Tipo de transacción",
      "keyword": null,
      "target_transaction_type": 1,
      "target_transaction_type_display": "Ingresos",
      "action_type": "assign_tag",
      "action_type_display": "Asignar etiqueta",
      "target_category": null,
      "target_category_name": null,
      "target_category_color": null,
      "target_category_icon": null,
      "target_tag": "ingreso",
      "is_active": true,
      "order": 2,
      "applied_count": 25,
      "created_at": "2025-11-23T11:00:00Z",
      "updated_at": "2025-11-23T15:00:00Z"
    }
  ]
}
```

**Respuesta cuando no hay reglas:**
```json
{
  "count": 0,
  "results": [],
  "message": "Aún no tienes reglas automáticas configuradas. ¡Crea una para automatizar la categorización de tus movimientos!"
}
```

---

### 2. Crear Regla Automática Nueva

**Método:** `POST`  
**URL:** `{{base_url}}/api/rules/`

**Headers:**
```
Authorization: {{token}}
Content-Type: application/json
```

**Body (JSON) - Regla por Descripción + Categoría:**
```json
{
  "name": "Uber y taxis",
  "criteria_type": "description_contains",
  "keyword": "uber",
  "action_type": "assign_category",
  "target_category": 5,
  "is_active": true,
  "order": 1
}
```

**Body (JSON) - Regla por Tipo + Etiqueta:**
```json
{
  "name": "Todos los ingresos",
  "criteria_type": "transaction_type",
  "target_transaction_type": 1,
  "action_type": "assign_tag",
  "target_tag": "ingreso",
  "is_active": true,
  "order": 2
}
```

**Body (JSON) - Regla Completa:**
```json
{
  "name": "Gastos de comida",
  "criteria_type": "description_contains",
  "keyword": "restaurante",
  "action_type": "assign_category",
  "target_category": 2,
  "is_active": true,
  "order": 3
}
```

**Respuesta Exitosa (201 Created):**
```json
{
  "id": 3,
  "name": "Gastos de comida",
  "criteria_type": "description_contains",
  "criteria_type_display": "Descripción contiene texto",
  "keyword": "restaurante",
  "target_transaction_type": null,
  "target_transaction_type_display": null,
  "action_type": "assign_category",
  "action_type_display": "Asignar categoría",
  "target_category": 2,
  "target_category_info": {
    "id": 2,
    "name": "Comida",
    "type": "expense",
    "type_display": "Gasto",
    "color": "#DC2626",
    "icon": "fa-utensils"
  },
  "target_tag": null,
  "is_active": true,
  "order": 3,
  "statistics": {
    "total_applied": 0,
    "last_applied": null,
    "avg_amount": null
  },
  "created_at": "2025-11-23T16:00:00Z",
  "updated_at": "2025-11-23T16:00:00Z"
}
```

**Errores Comunes (Formato Mejorado):**

```json
{
  "error": "Datos de entrada inválidos",
  "details": {
    "name": "Ya tienes una regla con este nombre."
  },
  "message": "Por favor corrige los siguientes errores:"
}
```

```json
{
  "error": "Datos de entrada inválidos", 
  "details": {
    "keyword": "La palabra clave es requerida para criterio \"descripción contiene texto\""
  },
  "message": "Por favor corrige los siguientes errores:"
}
```

```json
{
  "error": "Datos de entrada inválidos",
  "details": {
    "target_category": "La categoría con ID 5 no te pertenece. IDs de categorías disponibles: [1, 2, 3, 7, 8]. Usa GET /api/categories/ para ver tus categorías."
  },
  "message": "Por favor corrige los siguientes errores:"
}
```

---

### 3. Ver Detalle de una Regla

**Método:** `GET`  
**URL:** `{{base_url}}/api/rules/{id}/`

**Ejemplo:**
```
GET {{base_url}}/api/rules/1/
```

**Headers:**
```
Authorization: {{token}}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "id": 1,
  "name": "Uber y taxis",
  "criteria_type": "description_contains",
  "criteria_type_display": "Descripción contiene texto",
  "keyword": "uber",
  "target_transaction_type": null,
  "target_transaction_type_display": null,
  "action_type": "assign_category",
  "action_type_display": "Asignar categoría",
  "target_category": 5,
  "target_category_info": {
    "id": 5,
    "name": "Transporte",
    "type": "expense",
    "type_display": "Gasto",
    "color": "#EA580C",
    "icon": "fa-car"
  },
  "target_tag": null,
  "is_active": true,
  "order": 1,
  "statistics": {
    "total_applied": 12,
    "last_applied": "2025-11-23T15:30:00Z",
    "avg_amount": 15000.50
  },
  "created_at": "2025-11-23T10:00:00Z",
  "updated_at": "2025-11-23T14:30:00Z"
}
```

---

### 4. Actualizar Regla (PATCH)

**Método:** `PATCH`  
**URL:** `{{base_url}}/api/rules/{id}/`

**Ejemplo:**
```
PATCH {{base_url}}/api/rules/1/
```

**Headers:**
```
Authorization: {{token}}
Content-Type: application/json
```

**Body (JSON) - Cambiar palabra clave:**
```json
{
  "keyword": "taxi"
}
```

**Body (JSON) - Cambiar categoría objetivo:**
```json
{
  "target_category": 8
}
```

**Body (JSON) - Desactivar:**
```json
{
  "is_active": false
}
```

**Body (JSON) - Cambiar prioridad:**
```json
{
  "order": 5
}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "id": 1,
  "name": "Uber y taxis",
  "criteria_type": "description_contains",
  "criteria_type_display": "Descripción contiene texto",
  "keyword": "taxi",
  "target_transaction_type": null,
  "target_transaction_type_display": null,
  "action_type": "assign_category",
  "action_type_display": "Asignar categoría",
  "target_category": 8,
  "target_category_info": {
    "id": 8,
    "name": "Entretenimiento",
    "type": "expense",
    "type_display": "Gasto",
    "color": "#C2410C",
    "icon": "fa-film"
  },
  "target_tag": null,
  "is_active": true,
  "order": 1,
  "statistics": {
    "total_applied": 12,
    "last_applied": "2025-11-23T15:30:00Z",
    "avg_amount": 15000.50
  },
  "created_at": "2025-11-23T10:00:00Z",
  "updated_at": "2025-11-23T17:00:00Z"
}
```

---

### 5. Eliminar Regla

**Método:** `DELETE`  
**URL:** `{{base_url}}/api/rules/{id}/`

**Ejemplo:**
```
DELETE {{base_url}}/api/rules/3/
```

**Headers:**
```
Authorization: {{token}}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "message": "Regla \"Gastos de comida\" eliminada. Se limpiaron 5 transacciones afectadas.",
  "deleted_rule": "Gastos de comida",
  "affected_transactions": 5
}
```

---

## 🔧 Acciones Especiales

### 6. Activar/Desactivar Regla

**Método:** `POST`  
**URL:** `{{base_url}}/api/rules/{id}/toggle_active/`

**Ejemplo:**
```
POST {{base_url}}/api/rules/1/toggle_active/
```

**Headers:**
```
Authorization: {{token}}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "message": "Regla \"Uber y taxis\" desactivada exitosamente.",
  "rule": {
    "id": 1,
    "name": "Uber y taxis",
    "criteria_type": "description_contains",
    "is_active": false,
    "order": 1,
    "updated_at": "2025-11-23T17:30:00Z"
  }
}
```

---

### 7. Obtener Estadísticas Generales

**Método:** `GET`  
**URL:** `{{base_url}}/api/rules/stats/`

**Headers:**
```
Authorization: {{token}}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "total_rules": 5,
  "active_rules": 4,
  "inactive_rules": 1,
  "total_applications": 42,
  "most_used_rule": {
    "id": 2,
    "name": "Todos los ingresos",
    "applications": 25
  },
  "recent_applications": [
    {
      "transaction_id": 15,
      "rule_name": "Uber y taxis",
      "amount": 12000,
      "date": "2025-11-23",
      "created_at": "2025-11-23T17:45:00Z"
    },
    {
      "transaction_id": 14,
      "rule_name": "Todos los ingresos",
      "amount": 500000,
      "date": "2025-11-23",
      "created_at": "2025-11-23T16:30:00Z"
    }
  ]
}
```

---

### 8. Reordenar Reglas (Prioridad)

**Método:** `POST`  
**URL:** `{{base_url}}/api/rules/reorder/`

**Headers:**
```
Authorization: {{token}}
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "rule_orders": [
    {"id": 2, "order": 1},
    {"id": 1, "order": 2},
    {"id": 3, "order": 3}
  ]
}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "message": "3 reglas reordenadas exitosamente.",
  "rules": [
    {
      "id": 2,
      "name": "Todos los ingresos",
      "order": 1,
      "is_active": true
    },
    {
      "id": 1,
      "name": "Uber y taxis", 
      "order": 2,
      "is_active": true
    },
    {
      "id": 3,
      "name": "Gastos de comida",
      "order": 3,
      "is_active": true
    }
  ]
}
```

---

### 9. Previsualizar Aplicación de Reglas

**Método:** `POST`  
**URL:** `{{base_url}}/api/rules/preview/`

**Headers:**
```
Authorization: {{token}}
Content-Type: application/json
```

**Body (JSON) - Por descripción:**
```json
{
  "description": "Pago Uber Centro"
}
```

**Body (JSON) - Por tipo de transacción:**
```json
{
  "transaction_type": 1
}
```

**Body (JSON) - Ambos criterios:**
```json
{
  "description": "Salario mes noviembre",
  "transaction_type": 1
}
```

**Respuesta Exitosa (200 OK) - Se aplicará regla:**
```json
{
  "will_apply": true,
  "rule": {
    "id": 1,
    "name": "Uber y taxis",
    "action_type": "assign_category",
    "target_category": "Transporte",
    "target_tag": null
  },
  "message": "Se aplicará la regla \"Uber y taxis\""
}
```

**Respuesta (200 OK) - No se aplicará regla:**
```json
{
  "will_apply": false,
  "rule": null,
  "message": "No hay reglas que coincidan con estos criterios"
}
```

---

### 10. Obtener Solo Reglas Activas

**Método:** `GET`  
**URL:** `{{base_url}}/api/rules/active/`

**Headers:**
```
Authorization: {{token}}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "count": 4,
  "results": [
    {
      "id": 2,
      "name": "Todos los ingresos",
      "criteria_type": "transaction_type",
      "action_type": "assign_tag",
      "is_active": true,
      "order": 1
    },
    {
      "id": 1,
      "name": "Uber y taxis",
      "criteria_type": "description_contains",
      "action_type": "assign_category",
      "is_active": true,
      "order": 2
    }
  ],
  "message": "Reglas activas ordenadas por prioridad"
}
```

---

### 11. Ver Transacciones Aplicadas por Regla

**Método:** `GET`  
**URL:** `{{base_url}}/api/rules/{id}/applied_transactions/`

**Ejemplo:**
```
GET {{base_url}}/api/rules/1/applied_transactions/
```

**Headers:**
```
Authorization: {{token}}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "rule_name": "Uber y taxis",
  "total_applied": 12,
  "recent_transactions": [
    {
      "id": 15,
      "total_amount": 12000,
      "date": "2025-11-23",
      "description": "Uber viaje centro",
      "type": "Expense",
      "created_at": "2025-11-23T17:45:00Z"
    },
    {
      "id": 13,
      "total_amount": 8500,
      "date": "2025-11-22", 
      "description": "Taxi aeropuerto",
      "type": "Expense",
      "created_at": "2025-11-22T20:15:00Z"
    }
  ]
}
```

---

## 🔄 Integración con Transacciones

### Crear Transacción con Aplicación Automática de Reglas

**Método:** `POST`  
**URL:** `{{base_url}}/api/transactions/`

**Headers:**
```
Authorization: {{token}}
Content-Type: application/json
```

**Body (JSON) - Transacción que activará regla:**
```json
{
  "origin_account": 1,
  "type": 2,
  "base_amount": 15000,
  "date": "2025-11-23",
  "description": "Uber viaje trabajo",
  "tag": "transporte"
}
```

**Respuesta (201 Created) - Con regla aplicada automáticamente:**
```json
{
  "id": 16,
  "user": 1,
  "origin_account": 1,
  "type": 2,
  "base_amount": 15000,
  "total_amount": 15000,
  "date": "2025-11-23",
  "description": "Uber viaje trabajo",
  "tag": "transporte",
  "category": {
    "id": 5,
    "name": "Transporte",
    "color": "#EA580C"
  },
  "applied_rule": {
    "id": 1,
    "name": "Uber y taxis"
  },
  "created_at": "2025-11-23T18:00:00Z"
}
```

---

## 📊 Casos de Uso Completos

### Caso 1: Configurar Regla para Gastos de Transporte

**Paso 1: Verificar categorías disponibles**
```
GET {{base_url}}/api/categories/?type=expense
```

**Paso 2: Crear regla**
```
POST {{base_url}}/api/rules/
Content-Type: application/json

{
  "name": "Gastos Uber/Taxi",
  "criteria_type": "description_contains",
  "keyword": "uber",
  "action_type": "assign_category",
  "target_category": 5,
  "is_active": true,
  "order": 1
}
```

**Paso 3: Probar previsualización**
```
POST {{base_url}}/api/rules/preview/

{
  "description": "Pago Uber Centro"
}
```

**Paso 4: Crear transacción de prueba**
```
POST {{base_url}}/api/transactions/

{
  "origin_account": 1,
  "type": 2,
  "base_amount": 12000,
  "date": "2025-11-23", 
  "description": "Uber viaje oficina"
}
```

---

### Caso 2: Configurar Regla para Todos los Ingresos

**Paso 1: Crear regla de tipo transacción**
```
POST {{base_url}}/api/rules/

{
  "name": "Etiquetar ingresos",
  "criteria_type": "transaction_type",
  "target_transaction_type": 1,
  "action_type": "assign_tag",
  "target_tag": "ingreso",
  "is_active": true,
  "order": 1
}
```

**Paso 2: Probar con transacción de ingreso**
```
POST {{base_url}}/api/transactions/

{
  "origin_account": 1,
  "type": 1,
  "base_amount": 500000,
  "date": "2025-11-23",
  "description": "Salario noviembre"
}
```

---

### Caso 3: Gestionar Prioridades de Reglas

**Paso 1: Ver reglas actuales**
```
GET {{base_url}}/api/rules/active/
```

**Paso 2: Reordenar por prioridad**
```
POST {{base_url}}/api/rules/reorder/

{
  "rule_orders": [
    {"id": 3, "order": 1},
    {"id": 1, "order": 2},
    {"id": 2, "order": 3}
  ]
}
```

**Paso 3: Verificar estadísticas**
```
GET {{base_url}}/api/rules/stats/
```

---

## 🎨 Interpretación de Tipos

### Tipos de Criterio

| Tipo | Valor | Descripción |
|------|-------|-------------|
| Descripción contiene | `description_contains` | Busca palabra clave en la descripción |
| Tipo de transacción | `transaction_type` | Aplica a todas las transacciones del tipo seleccionado |

### Tipos de Acción

| Tipo | Valor | Descripción |
|------|-------|-------------|
| Asignar categoría | `assign_category` | Asigna una categoría específica |
| Asignar etiqueta | `assign_tag` | Asigna una etiqueta de texto |

### Tipos de Transacción

| Tipo | Valor | Descripción |
|------|-------|-------------|
| Ingresos | `1` | Entradas de dinero |
| Gastos | `2` | Salidas de dinero |
| Transferencias | `3` | Movimientos entre cuentas |
| Ahorros | `4` | Movimientos de ahorro |

---

## ❌ Manejo Mejorado de Errores

### 🎯 Nuevo Formato de Error (HU-12)

Todos los errores ahora devuelven un formato JSON consistente y útil:

```json
{
  "error": "Tipo de error principal",
  "message": "Descripción del problema",
  "details": {
    "campo": "Error específico del campo"
  },
  "suggestion": "Sugerencia para resolver el problema",
  "status_code": 400
}
```

### Error 401 Unauthorized

**Nueva Respuesta:**
```json
{
  "error": true,
  "message": "Error en la petición",
  "details": {
    "detail": "Token de autenticación inválido."
  },
  "status_code": 401,
  "suggestion": "Incluye el token de autenticación en el header Authorization"
}
```

**Causa:** Token no válido o no enviado  
**Solución:** Verifica el header `Authorization: Token xxxxx`

### Error 400 - Nombre duplicado

**Nueva Respuesta:**
```json
{
  "error": "Datos de entrada inválidos",
  "details": {
    "name": "Ya tienes una regla con este nombre."
  },
  "message": "Por favor corrige los siguientes errores:"
}
```

**Causa:** Ya existe una regla con ese nombre para el usuario  
**Solución:** Usa un nombre diferente o actualiza la regla existente

### Error 400 - Campos requeridos

**Nueva Respuesta:**
```json
{
  "error": "Datos de entrada inválidos",
  "details": {
    "keyword": "La palabra clave es requerida para criterio \"descripción contiene texto\"",
    "target_category": "La categoría objetivo es requerida para acción \"asignar categoría\""
  },
  "message": "Por favor corrige los siguientes errores:"
}
```

**Causa:** Falta keyword para criterio de descripción o target_category para acción de categoría  
**Solución:** Proporciona todos los campos requeridos según el tipo

### Error 400 - Categoría no válida

**Nueva Respuesta (Con IDs Disponibles):**
```json
{
  "error": "Datos de entrada inválidos",
  "details": {
    "target_category": "La categoría con ID 5 no te pertenece. IDs de categorías disponibles: [1, 2, 3, 7, 8]. Usa GET /api/categories/ para ver tus categorías."
  },
  "message": "Por favor corrige los siguientes errores:"
}
```

**Causa:** La categoría no pertenece al usuario autenticado  
**Solución:** Usa uno de los IDs mostrados en el mensaje o consulta GET /api/categories/

### Error 404 - Regla no encontrada

**Nueva Respuesta:**
```json
{
  "error": true,
  "message": "Error en la petición",
  "details": {
    "detail": "No encontrado."
  },
  "status_code": 404,
  "suggestion": "Verifica que el ID del recurso sea correcto y te pertenezca"
}
```

**Causa:** El ID no existe o pertenece a otro usuario  
**Solución:** Verifica el ID con GET /api/rules/

### Error 500 - Error interno

**Nueva Respuesta:**
```json
{
  "error": "Error interno al crear la regla",
  "message": "Descripción específica del error",
  "details": {
    "type": "ValidationError",
    "suggestion": "Verifica que todos los campos requeridos estén presentes y sean válidos"
  }
}
```

**Causa:** Error inesperado en el servidor  
**Solución:** Revisa los datos enviados y reintenta. Si persiste, contacta al administrador.

---

## 📝 Notas Importantes

1. **Orden de prioridad:** Las reglas se aplican según el campo `order` (menor número = mayor prioridad)
2. **Solo una regla por transacción:** Si varias reglas coinciden, solo se aplica la primera por prioridad
3. **Aplicación automática:** Las reglas se aplican automáticamente al crear nuevas transacciones
4. **Búsqueda insensible:** Las búsquedas por palabra clave no distinguen mayúsculas/minúsculas
5. **Categorías del usuario:** Solo puedes asignar categorías que te pertenecen
6. **Reglas inactivas:** Las reglas desactivadas no se aplican a nuevas transacciones
7. **Limpieza al eliminar:** Al eliminar una regla, se limpia la referencia en transacciones afectadas

---

## 🚀 Colección de Postman

Puedes importar esta estructura en Postman:

```
📁 Finanzas Backend - Rules API (HU-12)
  📁 Auth
    ├─ POST Login
  📁 CRUD Básico
    ├─ GET Listar Reglas
    ├─ POST Crear Regla
    ├─ GET Detalle Regla
    ├─ PATCH Actualizar Regla
    └─ DELETE Eliminar Regla
  📁 Gestión Avanzada
    ├─ POST Activar/Desactivar
    ├─ POST Reordenar Reglas
    ├─ POST Previsualizar Aplicación
    ├─ GET Solo Reglas Activas
    └─ GET Transacciones Aplicadas
  📁 Estadísticas
    └─ GET Estadísticas Generales
  📁 Integración
    └─ POST Crear Transacción (con reglas automáticas)
```

---

## 🎯 Ejemplos de Integración con Frontend

### Dashboard de Reglas
```javascript
// Obtener estadísticas para mostrar en dashboard
fetch('/api/rules/stats/', {
  headers: { 'Authorization': `Token ${token}` }
})
.then(res => res.json())
.then(data => {
  // Mostrar métricas
  document.getElementById('total-rules').textContent = data.total_rules;
  document.getElementById('active-rules').textContent = data.active_rules;
  document.getElementById('applications').textContent = data.total_applications;
  
  // Mostrar regla más usada
  if (data.most_used_rule.name) {
    showMostUsedRule(data.most_used_rule);
  }
});
```

### Previsualización en Formulario de Transacción
```javascript
// Previsualizar regla mientras el usuario escribe
const descriptionInput = document.getElementById('description');
descriptionInput.addEventListener('input', debounce(async (e) => {
  if (e.target.value.length > 3) {
    const preview = await fetch('/api/rules/preview/', {
      method: 'POST',
      headers: { 
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        description: e.target.value,
        transaction_type: getSelectedTransactionType()
      })
    }).then(res => res.json());
    
    if (preview.will_apply) {
      showRulePreview(preview.rule);
    } else {
      hideRulePreview();
    }
  }
}, 500));
```

---

**¡Happy Testing! 🎉**