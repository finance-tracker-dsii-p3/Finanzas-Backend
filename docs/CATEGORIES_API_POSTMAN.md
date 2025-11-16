# 📁 API de Categorías - Guía de Postman

Esta guía te ayudará a probar todos los endpoints de la API de **Categorías de Ingresos y Gastos** (HU-05) usando Postman.

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

**Respuesta:**
```json
{
  "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
  "user": {
    "id": 1,
    "email": "usuario@ejemplo.com",
    "first_name": "Juan",
    "last_name": "Pérez"
  }
}
```

---

## 📋 Endpoints CRUD Básicos

### 1. Listar Categorías

**Método:** `GET`  
**URL:** `{{base_url}}/api/categories/`

**Headers:**
```
Authorization: {{token}}
```

**Query Parameters (Opcionales):**
- `active_only=true` - Solo categorías activas (default)
- `active_only=false` - Incluir categorías inactivas
- `type=income` - Solo categorías de ingresos
- `type=expense` - Solo categorías de gastos

**Ejemplo con filtros:**
```
GET {{base_url}}/api/categories/?active_only=true&type=expense
```

**Respuesta Exitosa (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Comida",
    "type": "expense",
    "type_display": "Gasto",
    "color": "#EF4444",
    "icon": "fa-utensils",
    "icon_display": "Comida",
    "is_active": true,
    "order": 1,
    "usage_count": 15
  },
  {
    "id": 2,
    "name": "Salario",
    "type": "income",
    "type_display": "Ingreso",
    "color": "#10B981",
    "icon": "fa-money-bill-wave",
    "icon_display": "Dinero",
    "is_active": true,
    "order": 1,
    "usage_count": 12
  }
]
```

---

### 2. Crear Categoría Nueva

**Método:** `POST`  
**URL:** `{{base_url}}/api/categories/`

**Headers:**
```
Authorization: {{token}}
Content-Type: application/json
```

**Body (JSON) - Categoría de Gasto:**
```json
{
  "name": "Comida",
  "type": "expense",
  "color": "#EF4444",
  "icon": "fa-utensils",
  "is_active": true,
  "order": 1
}
```

**Body (JSON) - Categoría de Ingreso:**
```json
{
  "name": "Salario",
  "type": "income",
  "color": "#10B981",
  "icon": "fa-money-bill-wave",
  "is_active": true,
  "order": 1
}
```

**Body (JSON) - Con valores mínimos:**
```json
{
  "name": "Transporte",
  "type": "expense"
}
```
> Nota: `color`, `icon`, `is_active` y `order` son opcionales. Se usan valores por defecto.

**Respuesta Exitosa (201 Created):**
```json
{
  "id": 3,
  "name": "Comida",
  "description": null,
  "type": "expense",
  "type_display": "Gasto",
  "color": "#EF4444",
  "icon": "fa-utensils",
  "icon_display": "Comida",
  "is_active": true,
  "is_default": false,
  "order": 1,
  "related_data": {
    "transactions_count": 0,
    "budgets_count": 0,
    "can_be_deleted": true,
    "usage_count": 0
  },
  "created_at": "2025-11-15T10:30:00Z",
  "updated_at": "2025-11-15T10:30:00Z"
}
```

**Errores Comunes:**
```json
{
  "name": ["Ya tienes una categoría de Gasto llamada \"Comida\""]
}
```

```json
{
  "name": ["El nombre debe tener al menos 2 caracteres."]
}
```

```json
{
  "color": ["#FFF no es un código de color hexadecimal válido. Debe ser formato #RRGGBB"]
}
```

---

### 3. Ver Detalle de una Categoría

**Método:** `GET`  
**URL:** `{{base_url}}/api/categories/{id}/`

**Ejemplo:**
```
GET {{base_url}}/api/categories/1/
```

**Headers:**
```
Authorization: {{token}}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "id": 1,
  "name": "Comida",
  "type": "expense",
  "type_display": "Gasto",
  "color": "#EF4444",
  "icon": "fa-utensils",
  "icon_display": "Comida",
  "is_active": true,
  "is_default": false,
  "order": 1,
  "related_data": {
    "transactions_count": 15,
    "budgets_count": 2,
    "can_be_deleted": false,
    "usage_count": 17
  },
  "created_at": "2025-11-10T08:00:00Z",
  "updated_at": "2025-11-15T10:30:00Z"
}
```

---

### 4. Actualizar Categoría (PATCH)

**Método:** `PATCH`  
**URL:** `{{base_url}}/api/categories/{id}/`

**Ejemplo:**
```
PATCH {{base_url}}/api/categories/1/
```

**Headers:**
```
Authorization: {{token}}
Content-Type: application/json
```

**Body (JSON) - Cambiar solo el nombre:**
```json
{
  "name": "Comida y Bebidas"
}
```

**Body (JSON) - Cambiar color e ícono:**
```json
{
  "color": "#F59E0B",
  "icon": "fa-hamburger"
}
```

**Body (JSON) - Cambiar orden:**
```json
{
  "order": 5
}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "id": 1,
  "name": "Comida Y Bebidas",
  "type": "expense",
  "type_display": "Gasto",
  "color": "#F59E0B",
  "icon": "fa-hamburger",
  "icon_display": "Comida rápida",
  "is_active": true,
  "is_default": false,
  "order": 5,
  "related_data": {
    "transactions_count": 15,
    "budgets_count": 2,
    "can_be_deleted": false,
    "usage_count": 17
  },
  "created_at": "2025-11-10T08:00:00Z",
  "updated_at": "2025-11-15T12:00:00Z"
}
```

**Errores Comunes:**
```json
{
  "error": "No puedes editar una categoría del sistema."
}
```

```json
{
  "name": ["Ya tienes otra categoría de Gasto llamada \"Comida\""]
}
```

---

### 5. Eliminar Categoría (sin datos relacionados)

**Método:** `DELETE`  
**URL:** `{{base_url}}/api/categories/{id}/`

**Ejemplo:**
```
DELETE {{base_url}}/api/categories/3/
```

**Headers:**
```
Authorization: {{token}}
```

**Respuesta Exitosa (204 No Content):**
```
(Sin contenido - código 204)
```

**Error - Categoría tiene datos relacionados:**
```json
{
  "detail": "Esta categoría tiene transacciones o presupuestos asociados. Usa el endpoint /delete_with_reassignment/ para reasignarlos."
}
```

---

## 🔧 Acciones Especiales

### 6. Eliminar Categoría con Reasignación

**Método:** `POST`  
**URL:** `{{base_url}}/api/categories/{id}/delete_with_reassignment/`

**Ejemplo:**
```
POST {{base_url}}/api/categories/1/delete_with_reassignment/
```

**Headers:**
```
Authorization: {{token}}
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "target_category_id": 5
}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "reassigned_transactions": 15,
  "reassigned_budgets": 2,
  "category_name": "Comida"
}
```

**Errores:**
```json
{
  "target_category_id": ["La categoría destino no existe o no te pertenece."]
}
```

```json
{
  "target_category_id": ["La categoría destino debe ser del mismo tipo (Gasto)"]
}
```

---

### 7. Activar/Desactivar Categoría

**Método:** `POST`  
**URL:** `{{base_url}}/api/categories/{id}/toggle_active/`

**Ejemplo:**
```
POST {{base_url}}/api/categories/1/toggle_active/
```

**Headers:**
```
Authorization: {{token}}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "id": 1,
  "name": "Comida",
  "type": "expense",
  "is_active": false,
  "updated_at": "2025-11-15T14:30:00Z"
}
```

**Error:**
```json
{
  "error": "No puedes desactivar categorías del sistema"
}
```

---

### 8. Validar si se Puede Eliminar

**Método:** `GET`  
**URL:** `{{base_url}}/api/categories/{id}/validate_deletion/`

**Ejemplo:**
```
GET {{base_url}}/api/categories/1/validate_deletion/
```

**Headers:**
```
Authorization: {{token}}
```

**Respuesta - Se puede eliminar:**
```json
{
  "can_delete": true,
  "requires_reassignment": false,
  "warnings": [],
  "errors": [],
  "related_data": {
    "transactions_count": 0,
    "budgets_count": 0,
    "can_be_deleted": true,
    "usage_count": 0
  }
}
```

**Respuesta - Requiere reasignación:**
```json
{
  "can_delete": true,
  "requires_reassignment": true,
  "warnings": [
    "Esta categoría tiene 15 transacciones y 2 presupuestos asociados. Deberás reasignarlos a otra categoría."
  ],
  "errors": [],
  "related_data": {
    "transactions_count": 15,
    "budgets_count": 2,
    "can_be_deleted": false,
    "usage_count": 17
  }
}
```

**Respuesta - No se puede eliminar:**
```json
{
  "can_delete": false,
  "requires_reassignment": false,
  "warnings": [],
  "errors": [
    "No puedes eliminar categorías del sistema"
  ],
  "related_data": {
    "transactions_count": 0,
    "budgets_count": 0,
    "can_be_deleted": true,
    "usage_count": 0
  }
}
```

---

### 9. Obtener Estadísticas de Categorías

**Método:** `GET`  
**URL:** `{{base_url}}/api/categories/stats/`

**Headers:**
```
Authorization: {{token}}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "total_categories": 15,
  "active_categories": 12,
  "inactive_categories": 3,
  "income_categories": 5,
  "expense_categories": 10,
  "most_used": [
    {
      "id": 1,
      "name": "Comida",
      "type": "expense",
      "color": "#EF4444",
      "icon": "fa-utensils"
    },
    {
      "id": 2,
      "name": "Transporte",
      "type": "expense",
      "color": "#F59E0B",
      "icon": "fa-car"
    }
  ],
  "least_used": [
    {
      "id": 10,
      "name": "Libros",
      "type": "expense",
      "color": "#8B5CF6",
      "icon": "fa-book"
    }
  ]
}
```

---

### 10. Listar Solo Categorías de Ingresos

**Método:** `GET`  
**URL:** `{{base_url}}/api/categories/income/`

**Headers:**
```
Authorization: {{token}}
```

**Respuesta Exitosa (200 OK):**
```json
[
  {
    "id": 2,
    "name": "Salario",
    "type": "income",
    "type_display": "Ingreso",
    "color": "#10B981",
    "icon": "fa-money-bill-wave",
    "icon_display": "Dinero",
    "is_active": true,
    "order": 1,
    "usage_count": 12
  },
  {
    "id": 7,
    "name": "Freelance",
    "type": "income",
    "type_display": "Ingreso",
    "color": "#3B82F6",
    "icon": "fa-briefcase",
    "icon_display": "Negocio",
    "is_active": true,
    "order": 2,
    "usage_count": 8
  }
]
```

---

### 11. Listar Solo Categorías de Gastos

**Método:** `GET`  
**URL:** `{{base_url}}/api/categories/expense/`

**Headers:**
```
Authorization: {{token}}
```

**Respuesta Exitosa (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Comida",
    "type": "expense",
    "type_display": "Gasto",
    "color": "#EF4444",
    "icon": "fa-utensils",
    "icon_display": "Comida",
    "is_active": true,
    "order": 1,
    "usage_count": 15
  },
  {
    "id": 3,
    "name": "Transporte",
    "type": "expense",
    "type_display": "Gasto",
    "color": "#F59E0B",
    "icon": "fa-car",
    "icon_display": "Transporte",
    "is_active": true,
    "order": 2,
    "usage_count": 10
  }
]
```

---

### 12. Crear Categorías Por Defecto

**Método:** `POST`  
**URL:** `{{base_url}}/api/categories/create_defaults/`

**Headers:**
```
Authorization: {{token}}
```

**Respuesta Exitosa (201 Created):**
```json
{
  "message": "15 categorías creadas exitosamente",
  "categories": [
    {
      "id": 1,
      "name": "Salario",
      "type": "income",
      "type_display": "Ingreso",
      "color": "#10B981",
      "icon": "fa-money-bill-wave",
      "icon_display": "Dinero",
      "is_active": true,
      "order": 1,
      "usage_count": 0
    },
    {
      "id": 2,
      "name": "Comida",
      "type": "expense",
      "type_display": "Gasto",
      "color": "#EF4444",
      "icon": "fa-utensils",
      "icon_display": "Comida",
      "is_active": true,
      "order": 1,
      "usage_count": 0
    }
    // ... más categorías
  ]
}
```

**Error - Ya tiene categorías:**
```json
{
  "error": "Ya tienes categorías creadas. No se pueden crear las predeterminadas."
}
```

---

### 13. Actualizar Orden de Múltiples Categorías

**Método:** `POST`  
**URL:** `{{base_url}}/api/categories/bulk_update_order/`

**Headers:**
```
Authorization: {{token}}
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "categories": [
    {"id": 1, "order": 3},
    {"id": 2, "order": 1},
    {"id": 3, "order": 2},
    {"id": 4, "order": 4}
  ]
}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "updated_count": 4,
  "message": "4 categorías actualizadas"
}
```

---

## 🎨 Colores e Íconos Disponibles

### Colores Recomendados (con buen contraste)

**Gastos:**
- `#DC2626` - Rojo oscuro (ratio 5.30:1) ✓
- `#EA580C` - Naranja oscuro (ratio 3.67:1) ✓
- `#B91C1C` - Rojo muy oscuro (ratio 7.34:1) ✓
- `#C2410C` - Naranja muy oscuro (ratio 5.15:1) ✓
- `#4B5563` - Gris oscuro (ratio 7.60:1) ✓

**Ingresos:**
- `#059669` - Verde oscuro (ratio 3.23:1) ✓
- `#047857` - Verde muy oscuro (ratio 4.13:1) ✓
- `#0D9488` - Turquesa oscuro (ratio 3.12:1) ✓
- `#14B8A6` - Turquesa (ratio 2.49:1) ⚠️ Bajo contraste
- `#10B981` - Verde (ratio 2.54:1) ⚠️ Bajo contraste

**Neutros:**
- `#2563EB` - Azul oscuro (ratio 4.87:1) ✓
- `#1D4ED8` - Azul muy oscuro (ratio 6.23:1) ✓
- `#7C3AED` - Morado oscuro (ratio 4.05:1) ✓
- `#4F46E5` - Índigo oscuro (ratio 5.38:1) ✓
- `#DB2777` - Rosa oscuro (ratio 4.15:1) ✓
- `#C026D3` - Fucsia (ratio 4.48:1) ✓

> ⚠️ **Nota importante:** Los colores con ratio menor a 3.0:1 serán rechazados por la validación de contraste.

### Íconos Font Awesome Disponibles

**Comida y Bebidas:**
- `fa-utensils` - Cubiertos
- `fa-hamburger` - Hamburguesa
- `fa-pizza-slice` - Pizza
- `fa-coffee` - Café
- `fa-wine-glass` - Copa de vino

**Transporte:**
- `fa-car` - Auto
- `fa-bus` - Bus
- `fa-taxi` - Taxi
- `fa-bicycle` - Bicicleta
- `fa-gas-pump` - Gasolinera
- `fa-plane` - Avión

**Hogar:**
- `fa-home` - Casa
- `fa-bolt` - Servicios
- `fa-couch` - Muebles
- `fa-tree` - Jardín

**Finanzas:**
- `fa-money-bill-wave` - Dinero
- `fa-wallet` - Billetera
- `fa-credit-card` - Tarjeta
- `fa-piggy-bank` - Alcancía
- `fa-chart-line` - Gráfico
- `fa-briefcase` - Maletín
- `fa-hand-holding-usd` - Inversión
- `fa-coins` - Monedas
- `fa-dollar-sign` - Dólar

**Otros:**
- `fa-shopping-cart` - Compras
- `fa-heart` - Salud
- `fa-graduation-cap` - Educación
- `fa-film` - Entretenimiento
- `fa-tshirt` - Ropa
- `fa-mobile-alt` - Teléfono
- `fa-gift` - Regalo
- `fa-gamepad` - Juegos
- `fa-book` - Libros
- `fa-music` - Música
- `fa-dumbbell` - Gym
- `fa-paw` - Mascotas
- `fa-question-circle` - Otros

---

## 🧪 Casos de Prueba Sugeridos

### Flujo Completo de Pruebas

1. **Autenticación**
   ```
   POST /api/auth/login/
   ```

2. **Crear Categorías Por Defecto**
   ```
   POST /api/categories/create_defaults/
   ```

3. **Listar Todas las Categorías**
   ```
   GET /api/categories/
   ```

4. **Crear Categoría de Gasto Personalizada**
   ```
   POST /api/categories/
   Body: {"name": "Café", "type": "expense", "color": "#B91C1C", "icon": "fa-coffee"}
   ```

5. **Crear Categoría de Ingreso Personalizada**
   ```
   POST /api/categories/
   Body: {"name": "Bonos", "type": "income", "color": "#059669", "icon": "fa-gift"}
   ```

6. **Filtrar Solo Gastos**
   ```
   GET /api/categories/expense/
   ```

7. **Filtrar Solo Ingresos**
   ```
   GET /api/categories/income/
   ```

8. **Ver Estadísticas**
   ```
   GET /api/categories/stats/
   ```

9. **Actualizar Nombre de Categoría**
   ```
   PATCH /api/categories/1/
   Body: {"name": "Alimentos y Bebidas"}
   ```

10. **Actualizar Orden de Categorías**
    ```
    POST /api/categories/bulk_update_order/
    Body: {"categories": [{"id": 1, "order": 1}, {"id": 2, "order": 2}]}
    ```

11. **Desactivar Categoría**
    ```
    POST /api/categories/5/toggle_active/
    ```

12. **Validar Eliminación**
    ```
    GET /api/categories/1/validate_deletion/
    ```

13. **Eliminar Categoría (si no tiene datos)**
    ```
    DELETE /api/categories/10/
    ```

---

## ❌ Errores Comunes y Soluciones

### Error 401 Unauthorized
**Causa:** Token no válido o no enviado  
**Solución:** Verifica el header `Authorization: Token xxxxx`

### Error 400 - Categoría duplicada
**Causa:** Ya existe una categoría con ese nombre y tipo  
**Solución:** Cambia el nombre o verifica tus categorías existentes

### Error 400 - Color inválido
**Causa:** El color no es formato hexadecimal válido  
**Solución:** Usa formato `#RRGGBB` (ej: `#EF4444`)

### Error 400 - Contraste insuficiente
**Causa:** El color es muy claro y no tiene buen contraste  
**Solución:** Usa colores más oscuros (ver lista recomendada)

### Error 400 - No se puede eliminar
**Causa:** La categoría tiene transacciones o presupuestos  
**Solución:** Usa `/delete_with_reassignment/` para reasignar primero

---

## 📝 Notas Importantes

1. **Categorías únicas por usuario:** No puedes tener dos categorías del mismo tipo con el mismo nombre
2. **Mismo nombre, diferentes tipos:** Puedes tener "Regalos" como ingreso Y como gasto
3. **Contraste accesible:** Todos los colores se validan para asegurar buena visibilidad
4. **Reasignación automática:** Al eliminar, las transacciones se reasignan automáticamente
5. **Orden personalizable:** Usa `order` para controlar el orden de visualización
6. **Categorías inactivas:** Las categorías inactivas no aparecen en selectores pero mantienen su historial

---

## 🚀 Colección de Postman

Puedes importar esta estructura en Postman:

```
📁 Finanzas Backend - Categories API
  📁 Auth
    ├─ POST Login
  📁 CRUD Básico
    ├─ GET Listar Categorías
    ├─ GET Listar Ingresos
    ├─ GET Listar Gastos
    ├─ POST Crear Categoría
    ├─ GET Detalle Categoría
    ├─ PATCH Actualizar Categoría
    └─ DELETE Eliminar Categoría
  📁 Gestión Avanzada
    ├─ POST Crear Categorías Por Defecto
    ├─ POST Eliminar con Reasignación
    ├─ POST Activar/Desactivar
    ├─ GET Validar Eliminación
    └─ POST Actualizar Orden Masivo
  📁 Estadísticas
    └─ GET Estadísticas de Categorías
```

---

**¡Happy Testing! 🎉**
