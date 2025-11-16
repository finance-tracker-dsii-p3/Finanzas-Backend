# 📊 API de Cuentas Financieras - Guía de Postman

Esta guía te ayudará a probar todos los endpoints de la API de **Cuentas Financieras** (HU-04) usando Postman.

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

**Configurar token:** Copia el token y guárdalo en la variable `token` como: `Token a1b2c3d4...`

---

## 📋 Endpoints CRUD Básicos

### 1. Listar Cuentas

**Método:** `GET`  
**URL:** `{{base_url}}/api/accounts/`

**Headers:**
```
Authorization: {{token}}
```

**Query Parameters (Opcionales):**
- `active_only=true` - Solo cuentas activas (default)
- `active_only=false` - Incluir cuentas inactivas
- `category=bank_account` - Filtrar por categoría
- `account_type=asset` - Filtrar por tipo (asset/liability)

**Ejemplo con filtros:**
```
GET {{base_url}}/api/accounts/?active_only=true&category=bank_account
```

**Respuesta Exitosa (200 OK):**
```json
[
  {
    "id": 1,
    "name": "Cuenta Ahorros Bancolombia",
    "account_type": "asset",
    "account_type_display": "Activo",
    "category": "savings_account",
    "category_display": "Cuenta de Ahorros",
    "current_balance": "1500000.00",
    "currency": "COP",
    "currency_display": "Pesos Colombianos",
    "is_active": true
  },
  {
    "id": 2,
    "name": "Tarjeta Visa",
    "account_type": "liability",
    "account_type_display": "Pasivo",
    "category": "credit_card",
    "category_display": "Tarjeta de Crédito",
    "current_balance": "-250000.00",
    "currency": "COP",
    "currency_display": "Pesos Colombianos",
    "is_active": true
  }
]
```

---

### 2. Crear Cuenta Nueva

**Método:** `POST`  
**URL:** `{{base_url}}/api/accounts/`

**Headers:**
```
Authorization: {{token}}
Content-Type: application/json
```

**Body (JSON) - Cuenta de Ahorros:**
```json
{
  "name": "Cuenta Ahorros Davivienda",
  "description": "Cuenta de ahorros para gastos personales",
  "account_type": "asset",
  "category": "savings_account",
  "current_balance": "2000000.00",
  "currency": "COP"
}
```

**Body (JSON) - Tarjeta de Crédito:**
```json
{
  "name": "Tarjeta MasterCard",
  "description": "Tarjeta de crédito principal",
  "account_type": "liability",
  "category": "credit_card",
  "current_balance": "0.00",
  "currency": "COP"
}
```

**Body (JSON) - Billetera en Dólares:**
```json
{
  "name": "Billetera USD",
  "description": "Efectivo en dólares",
  "account_type": "asset",
  "category": "wallet",
  "current_balance": "500.00",
  "currency": "USD"
}
```

**Respuesta Exitosa (201 Created):**
```json
{
  "id": 3,
  "name": "Cuenta Ahorros Davivienda",
  "description": "Cuenta de ahorros para gastos personales",
  "account_type": "asset",
  "account_type_display": "Activo",
  "category": "savings_account",
  "category_display": "Cuenta de Ahorros",
  "current_balance": "2000000.00",
  "currency": "COP",
  "currency_display": "Pesos Colombianos",
  "is_active": true,
  "created_at": "2025-11-15T10:30:00Z",
  "updated_at": "2025-11-15T10:30:00Z"
}
```

**Errores Comunes:**
```json
{
  "name": ["Este campo es requerido."],
  "account_type": ["Debe ser 'asset' o 'liability'."],
  "category": ["Categoría no válida."]
}
```

---

### 3. Ver Detalle de una Cuenta

**Método:** `GET`  
**URL:** `{{base_url}}/api/accounts/{id}/`

**Ejemplo:**
```
GET {{base_url}}/api/accounts/1/
```

**Headers:**
```
Authorization: {{token}}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "id": 1,
  "user": {
    "id": 5,
    "email": "usuario@ejemplo.com",
    "full_name": "Juan Pérez"
  },
  "name": "Cuenta Ahorros Bancolombia",
  "description": "Cuenta principal de ahorros",
  "account_type": "asset",
  "account_type_display": "Activo",
  "category": "savings_account",
  "category_display": "Cuenta de Ahorros",
  "current_balance": "1500000.00",
  "currency": "COP",
  "currency_display": "Pesos Colombianos",
  "is_active": true,
  "created_at": "2025-11-10T08:00:00Z",
  "updated_at": "2025-11-15T10:30:00Z"
}
```

**Error (404 Not Found):**
```json
{
  "detail": "No encontrado."
}
```

---

### 4. Actualizar Cuenta Completa (PUT)

**Método:** `PUT`  
**URL:** `{{base_url}}/api/accounts/{id}/`

**Ejemplo:**
```
PUT {{base_url}}/api/accounts/1/
```

**Headers:**
```
Authorization: {{token}}
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "name": "Cuenta Ahorros Bancolombia Premium",
  "description": "Cuenta de ahorros premium actualizada",
  "account_type": "asset",
  "category": "savings_account",
  "current_balance": "1800000.00",
  "currency": "COP",
  "is_active": true
}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "id": 1,
  "name": "Cuenta Ahorros Bancolombia Premium",
  "description": "Cuenta de ahorros premium actualizada",
  "account_type": "asset",
  "account_type_display": "Activo",
  "category": "savings_account",
  "category_display": "Cuenta de Ahorros",
  "current_balance": "1800000.00",
  "currency": "COP",
  "currency_display": "Pesos Colombianos",
  "is_active": true,
  "created_at": "2025-11-10T08:00:00Z",
  "updated_at": "2025-11-15T11:45:00Z"
}
```

---

### 5. Actualizar Cuenta Parcialmente (PATCH)

**Método:** `PATCH`  
**URL:** `{{base_url}}/api/accounts/{id}/`

**Ejemplo:**
```
PATCH {{base_url}}/api/accounts/1/
```

**Headers:**
```
Authorization: {{token}}
Content-Type: application/json
```

**Body (JSON) - Solo actualizar nombre:**
```json
{
  "name": "Cuenta Ahorros Nuevo Nombre"
}
```

**Body (JSON) - Solo actualizar descripción:**
```json
{
  "description": "Nueva descripción actualizada"
}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "id": 1,
  "name": "Cuenta Ahorros Nuevo Nombre",
  "description": "Cuenta principal de ahorros",
  "account_type": "asset",
  "current_balance": "1800000.00",
  "currency": "COP",
  "is_active": true,
  "updated_at": "2025-11-15T12:00:00Z"
}
```

---

### 6. Eliminar Cuenta

**Método:** `DELETE`  
**URL:** `{{base_url}}/api/accounts/{id}/`

**Ejemplo:**
```
DELETE {{base_url}}/api/accounts/3/
```

**Headers:**
```
Authorization: {{token}}
```

**Respuesta Exitosa (204 No Content):**
```
(Sin contenido - código 204)
```

**Error - Cuenta con saldo:**
```json
{
  "error": "No se puede eliminar la cuenta porque tiene saldo: 1500000.00 COP"
}
```

**Error - Cuenta con transacciones:**
```json
{
  "error": "No se puede eliminar la cuenta porque tiene transacciones asociadas. Primero debe eliminar todas las transacciones o transferir el saldo."
}
```

---

## 📊 Endpoints Especiales

### 7. Resumen Financiero del Usuario

**Método:** `GET`  
**URL:** `{{base_url}}/api/accounts/summary/`

**Headers:**
```
Authorization: {{token}}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "total_assets": "5000000.00",
  "total_liabilities": "800000.00",
  "net_worth": "4200000.00",
  "accounts_count": 5,
  "active_accounts_count": 4,
  "balances_by_currency": {
    "COP": {
      "assets": "4500000.00",
      "liabilities": "800000.00",
      "net": "3700000.00"
    },
    "USD": {
      "assets": "500.00",
      "liabilities": "0.00",
      "net": "500.00"
    }
  },
  "accounts_by_category": {
    "Cuenta de Ahorros": {
      "count": 2,
      "balance": "3000000.00"
    },
    "Cuenta Bancaria": {
      "count": 1,
      "balance": "1500000.00"
    },
    "Tarjeta de Crédito": {
      "count": 2,
      "balance": "-800000.00"
    }
  }
}
```

---

### 8. Filtrar Cuentas por Moneda

**Método:** `GET`  
**URL:** `{{base_url}}/api/accounts/by_currency/?currency=COP`

**Query Parameters:**
- `currency` (requerido): COP, USD, o EUR

**Headers:**
```
Authorization: {{token}}
```

**Ejemplo con USD:**
```
GET {{base_url}}/api/accounts/by_currency/?currency=USD
```

**Respuesta Exitosa (200 OK):**
```json
[
  {
    "id": 4,
    "name": "Billetera USD",
    "account_type": "asset",
    "category": "wallet",
    "current_balance": "500.00",
    "currency": "USD",
    "is_active": true
  }
]
```

**Error - Moneda no válida:**
```json
{
  "error": "Moneda JPY no válida"
}
```

**Error - Parámetro faltante:**
```json
{
  "error": "Parámetro currency es requerido"
}
```

---

### 9. Resumen de Tarjetas de Crédito

**Método:** `GET`  
**URL:** `{{base_url}}/api/accounts/credit_cards_summary/`

**Headers:**
```
Authorization: {{token}}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "cards_count": 2,
  "total_credit_limit": "0.00",
  "total_used_credit": "800000.00",
  "available_credit": "-800000.00",
  "utilization_percentage": 0.0
}
```

**Nota:** Si las tarjetas no tienen `credit_limit` definido, mostrará 0.

---

### 10. Estadísticas por Categorías

**Método:** `GET`  
**URL:** `{{base_url}}/api/accounts/categories_stats/`

**Headers:**
```
Authorization: {{token}}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "Cuenta de Ahorros": {
    "count": 2,
    "total_balance": "3000000.00",
    "accounts": [
      {
        "id": 1,
        "name": "Cuenta Ahorros Bancolombia",
        "balance": "1500000.00",
        "currency": "COP"
      },
      {
        "id": 3,
        "name": "Cuenta Ahorros Davivienda",
        "balance": "1500000.00",
        "currency": "COP"
      }
    ]
  },
  "Tarjeta de Crédito": {
    "count": 2,
    "total_balance": "800000.00",
    "accounts": [
      {
        "id": 2,
        "name": "Tarjeta Visa",
        "balance": "-250000.00",
        "currency": "COP"
      },
      {
        "id": 5,
        "name": "Tarjeta MasterCard",
        "balance": "-550000.00",
        "currency": "COP"
      }
    ]
  },
  "Billetera": {
    "count": 1,
    "total_balance": "500.00",
    "accounts": [
      {
        "id": 4,
        "name": "Billetera USD",
        "balance": "500.00",
        "currency": "USD"
      }
    ]
  }
}
```

---

### 11. Ajustar Saldo Manualmente

**Método:** `POST`  
**URL:** `{{base_url}}/api/accounts/{id}/update_balance/`

**Ejemplo:**
```
POST {{base_url}}/api/accounts/1/update_balance/
```

**Headers:**
```
Authorization: {{token}}
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "new_balance": "2000000.00",
  "reason": "Ajuste por error en registro inicial"
}
```

**Body (JSON) - Sin razón (opcional):**
```json
{
  "new_balance": "2500000.00"
}
```

**Respuesta Exitosa (200 OK):**
```json
{
  "id": 1,
  "name": "Cuenta Ahorros Bancolombia",
  "current_balance": "2000000.00",
  "currency": "COP",
  "updated_at": "2025-11-15T14:30:00Z"
}
```

**Error - Balance inválido:**
```json
{
  "new_balance": ["Este campo es requerido."]
}
```

---

### 12. Validar si se Puede Eliminar Cuenta

**Método:** `POST`  
**URL:** `{{base_url}}/api/accounts/{id}/validate_deletion/`

**Ejemplo:**
```
POST {{base_url}}/api/accounts/1/validate_deletion/
```

**Headers:**
```
Authorization: {{token}}
Content-Type: application/json
```

**Body (JSON) - Opcional:**
```json
{
  "force": false
}
```

**Respuesta - Se puede eliminar (200 OK):**
```json
{
  "can_delete": true,
  "requires_confirmation": false,
  "warnings": [],
  "errors": []
}
```

**Respuesta - Requiere confirmación:**
```json
{
  "can_delete": true,
  "requires_confirmation": true,
  "warnings": [
    "La cuenta tiene saldo: 1500000.00 COP",
    "Es la única cuenta en COP"
  ],
  "errors": []
}
```

**Respuesta - No se puede eliminar:**
```json
{
  "can_delete": false,
  "requires_confirmation": true,
  "warnings": [
    "La cuenta tiene 15 transacciones"
  ],
  "errors": [
    "La cuenta tiene transacciones asociadas y no puede ser eliminada"
  ]
}
```

---

### 13. Activar/Desactivar Cuenta

**Método:** `POST`  
**URL:** `{{base_url}}/api/accounts/{id}/toggle_active/`

**Ejemplo:**
```
POST {{base_url}}/api/accounts/1/toggle_active/
```

**Headers:**
```
Authorization: {{token}}
```

**Respuesta Exitosa - Desactivada (200 OK):**
```json
{
  "id": 1,
  "name": "Cuenta Ahorros Bancolombia",
  "is_active": false,
  "current_balance": "0.00",
  "updated_at": "2025-11-15T15:00:00Z"
}
```

**Respuesta Exitosa - Activada (200 OK):**
```json
{
  "id": 1,
  "name": "Cuenta Ahorros Bancolombia",
  "is_active": true,
  "current_balance": "0.00",
  "updated_at": "2025-11-15T15:05:00Z"
}
```

**Error - Cuenta con saldo:**
```json
{
  "error": "No se puede desactivar una cuenta con saldo"
}
```

---

## 🔍 Categorías y Tipos Disponibles

### Tipos de Cuenta (account_type)
- `asset` - Activo (dinero que tienes)
- `liability` - Pasivo (dinero que debes)

### Categorías (category)
- `bank_account` - Cuenta Bancaria
- `savings_account` - Cuenta de Ahorros
- `credit_card` - Tarjeta de Crédito
- `wallet` - Billetera (efectivo)
- `other` - Otro

### Monedas (currency)
- `COP` - Pesos Colombianos
- `USD` - Dólares
- `EUR` - Euros

---

## 🧪 Casos de Prueba Sugeridos

### Flujo Completo de Pruebas

1. **Autenticación**
   ```
   POST /api/auth/login/
   ```

2. **Crear Cuenta de Ahorros**
   ```
   POST /api/accounts/
   Body: {"name": "Mi Ahorro", "account_type": "asset", "category": "savings_account", "current_balance": "1000000", "currency": "COP"}
   ```

3. **Crear Tarjeta de Crédito**
   ```
   POST /api/accounts/
   Body: {"name": "Visa", "account_type": "liability", "category": "credit_card", "current_balance": "0", "currency": "COP"}
   ```

4. **Listar Todas las Cuentas**
   ```
   GET /api/accounts/
   ```

5. **Ver Resumen Financiero**
   ```
   GET /api/accounts/summary/
   ```

6. **Filtrar por Moneda**
   ```
   GET /api/accounts/by_currency/?currency=COP
   ```

7. **Ver Estadísticas por Categoría**
   ```
   GET /api/accounts/categories_stats/
   ```

8. **Actualizar Saldo**
   ```
   POST /api/accounts/1/update_balance/
   Body: {"new_balance": "1500000", "reason": "Depósito"}
   ```

9. **Validar Eliminación**
   ```
   POST /api/accounts/1/validate_deletion/
   ```

10. **Desactivar Cuenta (primero poner saldo en 0)**
    ```
    POST /api/accounts/1/update_balance/
    Body: {"new_balance": "0"}
    
    POST /api/accounts/1/toggle_active/
    ```

11. **Eliminar Cuenta**
    ```
    DELETE /api/accounts/1/
    ```

---

## ❌ Errores Comunes y Soluciones

### Error 401 Unauthorized
**Causa:** Token no válido o no enviado  
**Solución:** Verifica que el header `Authorization: Token xxxxx` esté configurado correctamente

### Error 403 Forbidden
**Causa:** No tienes permiso para acceder a esta cuenta (pertenece a otro usuario)  
**Solución:** Solo puedes acceder a tus propias cuentas

### Error 404 Not Found
**Causa:** La cuenta con ese ID no existe  
**Solución:** Verifica que el ID sea correcto con `GET /api/accounts/`

### Error 400 Bad Request
**Causa:** Datos enviados no válidos  
**Solución:** Revisa el formato JSON y los campos requeridos

### Error 500 Internal Server Error
**Causa:** Error en el servidor  
**Solución:** Revisa los logs del servidor Django

---

## 📝 Notas Importantes

1. **Autenticación requerida:** Todos los endpoints requieren token de autenticación
2. **Cuentas por usuario:** Solo puedes ver y gestionar tus propias cuentas
3. **Saldo cero para eliminar:** Las cuentas deben tener saldo 0 para ser eliminadas
4. **Activos vs Pasivos:** Los activos son positivos, los pasivos son negativos
5. **Monedas:** Cada cuenta tiene su propia moneda, no se pueden mezclar
6. **Desactivación:** Solo se pueden desactivar cuentas con saldo 0

---

## 🚀 Colección de Postman

Puedes importar esta estructura en Postman creando una nueva colección con las siguientes peticiones organizadas en carpetas:

```
📁 Finanzas Backend - Accounts API
  📁 Auth
    ├─ POST Login
  📁 CRUD Básico
    ├─ GET Listar Cuentas
    ├─ POST Crear Cuenta
    ├─ GET Detalle Cuenta
    ├─ PUT Actualizar Completa
    ├─ PATCH Actualizar Parcial
    └─ DELETE Eliminar Cuenta
  📁 Resúmenes y Estadísticas
    ├─ GET Resumen Financiero
    ├─ GET Por Moneda
    ├─ GET Resumen Tarjetas
    └─ GET Estadísticas Categorías
  📁 Acciones Especiales
    ├─ POST Ajustar Saldo
    ├─ POST Validar Eliminación
    └─ POST Activar/Desactivar
```

---

**¡Happy Testing! 🎉**