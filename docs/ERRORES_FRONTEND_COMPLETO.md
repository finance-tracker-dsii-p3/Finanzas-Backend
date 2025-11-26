# Guía Completa de Errores para Frontend

Este documento lista todos los errores HTTP y de validación que el frontend debe manejar para cada endpoint de la API.

---

## 📋 Índice

1. [Autenticación (`/api/auth/`)](#1-autenticación)
2. [Cuentas (`/api/accounts/`)](#2-cuentas)
3. [Categorías (`/api/categories/`)](#3-categorías)
4. [Presupuestos (`/api/budgets/`)](#4-presupuestos)
5. [Transacciones (`/api/transactions/`)](#5-transacciones)

---

## 1. Autenticación (`/api/auth/`)

### 1.1. `POST /api/auth/register/` - Registro de usuario

**Errores posibles:**

| Código | Campo | Mensaje | Descripción |
|--------|-------|---------|-------------|
| 400 | `password_confirm` | `"Las contraseñas no coinciden"` | Las contraseñas no son iguales |
| 400 | `identification` | `"Ya existe un usuario con esta identificación"` | Identificación duplicada |
| 400 | `username` | `"Ya existe un usuario con este nombre de usuario"` | Username duplicado |
| 400 | `email` | `"Ya existe un usuario con este email"` | Email duplicado |
| 400 | `email` | `"Enter a valid email address."` | Formato de email inválido |
| 400 | `password` | `"This field may not be blank."` | Contraseña vacía |
| 400 | `password` | `"This password is too short. It must contain at least 8 characters."` | Contraseña muy corta |
| 400 | `identification` | `"This field may not be blank."` | Identificación vacía |
| 400 | `username` | `"This field may not be blank."` | Username vacío |
| 400 | `first_name` | `"This field may not be blank."` | Nombre vacío |
| 400 | `last_name` | `"This field may not be blank."` | Apellido vacío |
| 401 | - | `"Authentication credentials were not provided."` | Sin token (si aplica) |

**Ejemplo de respuesta de error:**
```json
{
  "password_confirm": ["Las contraseñas no coinciden"],
  "email": ["Ya existe un usuario con este email"]
}
```

---

### 1.2. `POST /api/auth/login/` - Inicio de sesión

**Errores posibles:**

| Código | Campo | Mensaje | Descripción |
|--------|-------|---------|-------------|
| 400 | `username` | `"Usuario no encontrado"` | Usuario no existe |
| 400 | `username` | `"Cuenta desactivada"` | Usuario inactivo |
| 400 | `password` | `"Contraseña incorrecta"` | Contraseña inválida |
| 400 | `username` | `"Tu cuenta aún no ha sido verificada por un administrador"` | Usuario no verificado (solo usuarios regulares) |
| 400 | - | `"Debe incluir username y password"` | Campos faltantes |
| 400 | `username` | `"This field may not be blank."` | Username vacío |
| 400 | `password` | `"This field may not be blank."` | Contraseña vacía |

**Ejemplo de respuesta de error:**
```json
{
  "password": ["Contraseña incorrecta"]
}
```

---

### 1.3. `POST /api/auth/logout/` - Cerrar sesión

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | `"Authentication credentials were not provided."` | Sin token de autenticación |
| 401 | `"Invalid token."` | Token inválido o expirado |

---

### 1.4. `POST /api/auth/password/reset-request/` - Solicitar restablecimiento

**Errores posibles:**

| Código | Campo | Mensaje | Descripción |
|--------|-------|---------|-------------|
| 400 | `email` | `"This field may not be blank."` | Email vacío |
| 400 | `email` | `"Enter a valid email address."` | Formato de email inválido |
| 400 | `email` | `"No existe un usuario con este email"` | Email no registrado |

---

### 1.5. `GET /api/auth/password/reset-confirm/?token={token}` - Validar token

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 400 | `"Token inválido o expirado"` | Token no válido |
| 400 | `"Token no proporcionado"` | Falta el parámetro token |

---

### 1.6. `POST /api/auth/password/reset-confirm/` - Confirmar restablecimiento

**Errores posibles:**

| Código | Campo | Mensaje | Descripción |
|--------|-------|---------|-------------|
| 400 | `token` | `"Token inválido o expirado"` | Token no válido |
| 400 | `token` | `"This field is required."` | Token faltante |
| 400 | `password` | `"This field may not be blank."` | Contraseña vacía |
| 400 | `password` | `"This password is too short. It must contain at least 8 characters."` | Contraseña muy corta |
| 400 | `password_confirm` | `"Las contraseñas no coinciden"` | Contraseñas no coinciden |

---

### 1.7. `GET /api/auth/profile/` - Obtener perfil

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | `"Authentication credentials were not provided."` | Sin token |
| 401 | `"Invalid token."` | Token inválido |

---

### 1.8. `PATCH /api/auth/profile/update/` - Actualizar perfil

**Errores posibles:**

| Código | Campo | Mensaje | Descripción |
|--------|-------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 400 | `email` | `"Ya existe un usuario con este email"` | Email duplicado |
| 400 | `email` | `"Enter a valid email address."` | Email inválido |
| 400 | `username` | `"Ya existe un usuario con este nombre de usuario"` | Username duplicado |

---

### 1.9. `POST /api/auth/change-password/` - Cambiar contraseña

**Errores posibles:**

| Código | Campo | Mensaje | Descripción |
|--------|-------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 400 | `old_password` | `"Contraseña actual incorrecta"` | Contraseña actual incorrecta |
| 400 | `old_password` | `"This field is required."` | Contraseña actual faltante |
| 400 | `new_password` | `"This field is required."` | Nueva contraseña faltante |
| 400 | `new_password` | `"This password is too short. It must contain at least 8 characters."` | Nueva contraseña muy corta |
| 400 | `new_password_confirm` | `"Las contraseñas no coinciden"` | Contraseñas no coinciden |

---

### 1.10. `DELETE /api/auth/profile/delete/` - Eliminar cuenta

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | `"Authentication credentials were not provided."` | Sin token |
| 400 | `"No se puede eliminar la cuenta porque tiene saldo en alguna cuenta"` | Cuenta con saldo |
| 400 | `"No se puede eliminar la cuenta porque tiene transacciones asociadas"` | Tiene transacciones |
| 400 | `"Debe confirmar la eliminación proporcionando 'confirm': true"` | Falta confirmación |

---

## 2. Cuentas (`/api/accounts/`)

### 2.1. `GET /api/accounts/` - Listar cuentas

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | `"Authentication credentials were not provided."` | Sin token |

**Respuesta exitosa (sin cuentas):**
```json
{
  "count": 0,
  "results": []
}
```

---

### 2.2. `GET /api/accounts/{id}/` - Obtener cuenta

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | `"Authentication credentials were not provided."` | Sin token |
| 404 | `"Not found."` | Cuenta no existe o no pertenece al usuario |

---

### 2.3. `POST /api/accounts/` - Crear cuenta

**Errores posibles:**

| Código | Campo | Mensaje | Descripción |
|--------|-------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 400 | `name` | `"This field is required."` | Nombre faltante |
| 400 | `name` | `"Ya tienes una cuenta con este nombre"` | Nombre duplicado |
| 400 | `account_type` | `"This field is required."` | Tipo de cuenta faltante |
| 400 | `category` | `"This field is required."` | Categoría faltante |
| 400 | `currency` | `"This field is required."` | Moneda faltante |
| 400 | `current_balance` | `"Las tarjetas de crédito no pueden tener saldo positivo."` | Tarjeta con saldo positivo |
| 400 | `current_balance` | `"Las cuentas de pasivo deben tener saldo negativo o cero."` | Pasivo con saldo positivo |
| 400 | `current_balance` | `"Las cuentas de activo no pueden tener saldo negativo."` | Activo con saldo negativo |
| 400 | `credit_limit` | `"El límite de crédito debe ser mayor a cero."` | Límite inválido |
| 400 | `credit_limit` | `"El límite de crédito solo aplica para tarjetas de crédito."` | Límite en cuenta no tarjeta |
| 400 | `expiration_date` | `"La fecha de vencimiento solo aplica para tarjetas de crédito."` | Fecha en cuenta no tarjeta |
| 500 | - | `"Has alcanzado el límite máximo de cuentas (50)"` | Límite de cuentas alcanzado |

**Ejemplo de respuesta de error:**
```json
{
  "name": ["Ya tienes una cuenta con este nombre"],
  "current_balance": ["Las tarjetas de crédito no pueden tener saldo positivo."]
}
```

---

### 2.4. `PATCH /api/accounts/{id}/` - Actualizar cuenta

**Errores posibles:**

| Código | Campo | Mensaje | Descripción |
|--------|-------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 404 | - | `"Not found."` | Cuenta no existe |
| 400 | `name` | `"Ya tienes una cuenta con este nombre"` | Nombre duplicado |
| 400 | `account_type` | `"No puedes cambiar el tipo de cuenta cuando tiene saldo."` | Cambio de tipo con saldo |
| 400 | `currency` | `"No puedes cambiar la moneda cuando la cuenta tiene saldo."` | Cambio de moneda con saldo |
| 400 | `credit_limit` | `"El límite de crédito debe ser mayor a cero."` | Límite inválido |
| 400 | `credit_limit` | `"El límite de crédito solo aplica para tarjetas de crédito."` | Límite en cuenta no tarjeta |
| 400 | `expiration_date` | `"La fecha de vencimiento solo aplica para tarjetas de crédito."` | Fecha en cuenta no tarjeta |

---

### 2.5. `DELETE /api/accounts/{id}/` - Eliminar cuenta

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 404 | - | `"Not found."` | Cuenta no existe |
| 400 | - | `"No se puede eliminar la cuenta porque tiene saldo: {saldo} {moneda}"` | Cuenta con saldo |
| 400 | - | `"No se puede eliminar la cuenta porque tiene transacciones asociadas"` | Tiene transacciones |

---

### 2.6. `POST /api/accounts/{id}/validate_deletion/` - Validar eliminación

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 404 | - | `"Not found."` | Cuenta no existe |

**Respuesta exitosa:**
```json
{
  "can_delete": false,
  "errors": [
    "No se puede eliminar la cuenta porque tiene saldo: $1000.00 COP"
  ]
}
```

---

### 2.7. `POST /api/accounts/{id}/update_balance/` - Actualizar saldo

**Errores posibles:**

| Código | Campo | Mensaje | Descripción |
|--------|-------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 404 | - | `"Not found."` | Cuenta no existe |
| 400 | `new_balance` | `"This field is required."` | Saldo faltante |
| 400 | `new_balance` | `"Las tarjetas de crédito no pueden tener saldo positivo."` | Tarjeta con saldo positivo |
| 400 | `new_balance` | `"Las cuentas de pasivo no pueden tener saldo positivo."` | Pasivo con saldo positivo |
| 400 | `new_balance` | `"Las cuentas de activo no pueden tener saldo negativo."` | Activo con saldo negativo |

---

### 2.8. `POST /api/accounts/{id}/toggle_active/` - Activar/Desactivar

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 404 | - | `"Not found."` | Cuenta no existe |

---

### 2.9. `GET /api/accounts/options/` - Obtener opciones

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |

---

## 3. Categorías (`/api/categories/`)

### 3.1. `GET /api/categories/?{filters}` - Listar categorías

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |

**Respuesta exitosa (sin categorías):**
```json
{
  "count": 0,
  "message": "No tienes categorías creadas. Usa POST /api/categories/create_defaults/ para crear categorías por defecto.",
  "results": []
}
```

---

### 3.2. `GET /api/categories/{id}/` - Obtener categoría

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 404 | - | `"Not found."` | Categoría no existe o no pertenece al usuario |

---

### 3.3. `POST /api/categories/` - Crear categoría

**Errores posibles:**

| Código | Campo | Mensaje | Descripción |
|--------|-------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 400 | `name` | `"This field is required."` | Nombre faltante |
| 400 | `name` | `"El nombre debe tener al menos 2 caracteres."` | Nombre muy corto |
| 400 | `name` | `"El nombre no puede tener más de 100 caracteres."` | Nombre muy largo |
| 400 | `name` | `"Ya tienes una categoría de {tipo} llamada \"{nombre}\""` | Nombre duplicado para el mismo tipo |
| 400 | `type` | `"This field is required."` | Tipo faltante |
| 400 | `type` | `"\"{valor}\" is not a valid choice."` | Tipo inválido (debe ser 'income' o 'expense') |
| 400 | - | `"Debes estar autenticado para crear categorías."` | Usuario no autenticado |

**Ejemplo de respuesta de error:**
```json
{
  "name": ["Ya tienes una categoría de Gasto llamada \"Alimentación\""],
  "type": ["This field is required."]
}
```

---

### 3.4. `PATCH /api/categories/{id}/` - Actualizar categoría

**Errores posibles:**

| Código | Campo | Mensaje | Descripción |
|--------|-------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 404 | - | `"Not found."` | Categoría no existe |
| 400 | `name` | `"El nombre debe tener al menos 2 caracteres."` | Nombre muy corto |
| 400 | `name` | `"El nombre no puede tener más de 100 caracteres."` | Nombre muy largo |
| 400 | `name` | `"Ya tienes otra categoría de {tipo} llamada \"{nombre}\""` | Nombre duplicado |
| 400 | - | `"No puedes editar una categoría del sistema."` | Categoría por defecto (is_default=true) |

---

### 3.5. `POST /api/categories/{id}/toggle_active/` - Activar/Desactivar

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 404 | - | `"Not found."` | Categoría no existe |

---

### 3.6. `DELETE /api/categories/{id}/` - Eliminar categoría

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 404 | - | `"Not found."` | Categoría no existe |
| 400 | - | `"No se puede eliminar la categoría porque tiene transacciones asociadas"` | Tiene transacciones |
| 400 | - | `"No puedes eliminar una categoría del sistema."` | Categoría por defecto |

---

### 3.7. `POST /api/categories/{id}/delete_with_reassignment/` - Eliminar con reasignación

**Errores posibles:**

| Código | Campo | Mensaje | Descripción |
|--------|-------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 404 | - | `"Not found."` | Categoría no existe |
| 400 | `reassign_to` | `"This field is required."` | Categoría de reasignación faltante |
| 400 | `reassign_to` | `"La categoría de reasignación debe ser del mismo tipo."` | Tipo diferente |
| 400 | `reassign_to` | `"La categoría de reasignación no puede ser la misma que se está eliminando."` | Misma categoría |
| 400 | - | `"No puedes eliminar una categoría del sistema."` | Categoría por defecto |

---

### 3.8. `GET /api/categories/{id}/validate_deletion/` - Validar eliminación

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 404 | - | `"Not found."` | Categoría no existe |

**Respuesta exitosa:**
```json
{
  "can_delete": false,
  "errors": [
    "No se puede eliminar la categoría porque tiene 5 transacciones asociadas"
  ],
  "transaction_count": 5
}
```

---

### 3.9. `GET /api/categories/stats/` - Estadísticas

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |

---

### 3.10. `POST /api/categories/create_defaults/` - Crear categorías por defecto

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 400 | - | `"Ya tienes categorías creadas"` | Ya existen categorías |

---

### 3.11. `POST /api/categories/bulk_update_order/` - Actualizar orden

**Errores posibles:**

| Código | Campo | Mensaje | Descripción |
|--------|-------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 400 | `categories` | `"This field is required."` | Lista de categorías faltante |
| 400 | `categories` | `"Expected a list of items but got type \"dict\"."` | Formato incorrecto |

**Formato esperado:**
```json
{
  "categories": [
    {"id": 1, "order": 1},
    {"id": 2, "order": 2}
  ]
}
```

---

## 4. Presupuestos (`/api/budgets/`)

### 4.1. `GET /api/budgets/?{filters}` - Listar presupuestos

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |

**Respuesta exitosa (sin presupuestos):**
```json
{
  "count": 0,
  "message": "Aún no tienes límites definidos. ¡Agrega uno para empezar a controlar tus gastos!",
  "results": []
}
```

---

### 4.2. `GET /api/budgets/{id}/` - Obtener presupuesto

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 404 | - | `"Not found."` | Presupuesto no existe o no pertenece al usuario |

---

### 4.3. `POST /api/budgets/` - Crear presupuesto

**Errores posibles:**

| Código | Campo | Mensaje | Descripción |
|--------|-------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 400 | `category` | `"This field is required."` | Categoría faltante |
| 400 | `category` | `"La categoría no pertenece al usuario autenticado."` | Categoría de otro usuario |
| 400 | `category` | `"Solo se pueden crear presupuestos para categorías de gasto."` | Categoría no es de tipo gasto |
| 400 | `category` | `"Ya existe un presupuesto {período} para esta categoría."` | Presupuesto duplicado para categoría y período |
| 400 | `amount` | `"This field is required."` | Monto faltante |
| 400 | `amount` | `"El monto debe ser mayor a cero."` | Monto inválido (≤ 0) |
| 400 | `alert_threshold` | `"El umbral de alerta debe estar entre 0 y 100."` | Umbral fuera de rango |
| 400 | `period` | `"\"{valor}\" is not a valid choice."` | Período inválido (debe ser 'monthly' o 'yearly') |

**Ejemplo de respuesta de error:**
```json
{
  "category": ["Solo se pueden crear presupuestos para categorías de gasto."],
  "amount": ["El monto debe ser mayor a cero."]
}
```

---

### 4.4. `PATCH /api/budgets/{id}/` - Actualizar presupuesto

**Errores posibles:**

| Código | Campo | Mensaje | Descripción |
|--------|-------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 404 | - | `"Not found."` | Presupuesto no existe |
| 400 | `amount` | `"El monto debe ser mayor a cero."` | Monto inválido |
| 400 | `alert_threshold` | `"El umbral de alerta debe estar entre 0 y 100."` | Umbral fuera de rango |

---

### 4.5. `DELETE /api/budgets/{id}/` - Eliminar presupuesto

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 404 | - | `"Not found."` | Presupuesto no existe |

---

### 4.6. `POST /api/budgets/{id}/toggle_active/` - Activar/Desactivar

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 404 | - | `"Not found."` | Presupuesto no existe |

---

### 4.7. `GET /api/budgets/monthly_summary/` - Resumen mensual

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |

---

### 4.8. `GET /api/budgets/by_category/{categoryId}/?{filters}` - Por categoría

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 404 | - | `"Not found."` | Categoría no existe o no pertenece al usuario |

---

### 4.9. `GET /api/budgets/categories_without_budget/?{filters}` - Categorías sin presupuesto

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |

---

### 4.10. `GET /api/budgets/alerts/` - Alertas

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |

---

## 5. Transacciones (`/api/transactions/`)

### 5.1. `GET /api/transactions/?{filters}` - Listar transacciones

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |

**Respuesta exitosa:**
```json
{
  "count": 0,
  "results": []
}
```

---

### 5.2. `GET /api/transactions/{id}/` - Obtener transacción

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 404 | - | `"Not found."` | Transacción no existe o no pertenece al usuario |

---

### 5.3. `POST /api/transactions/` - Crear transacción

**Errores posibles:**

| Código | Campo | Mensaje | Descripción |
|--------|-------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 400 | `origin_account` | `"This field is required."` | Cuenta origen faltante |
| 400 | `category` | `"This field is required."` | Categoría faltante (para ingresos/gastos) |
| 400 | `category` | `"La categoría no pertenece al usuario autenticado."` | Categoría de otro usuario |
| 400 | `category` | `"La categoría debe ser de tipo \"Ingreso\" para transacciones de ingreso."` | Tipo de categoría incorrecto (ingreso) |
| 400 | `category` | `"La categoría debe ser de tipo \"Gasto\" para transacciones de gasto."` | Tipo de categoría incorrecto (gasto) |
| 400 | `category` | `"Las transferencias no deben tener categoría asignada."` | Categoría en transferencia |
| 400 | `type` | `"This field is required."` | Tipo de transacción faltante |
| 400 | `type` | `"\"{valor}\" is not a valid choice."` | Tipo inválido (debe ser 1, 2, 3 o 4) |
| 400 | `base_amount` | `"El monto base debe ser un valor positivo mayor que cero."` | Monto base inválido |
| 400 | `total_amount` | `"El monto total debe ser un valor positivo mayor que cero."` | Monto total inválido |
| 400 | `base_amount` | `"No se puede proporcionar base_amount y total_amount simultáneamente. Use uno u otro."` | Ambos campos enviados |
| 400 | `total_amount` | `"No se puede proporcionar base_amount y total_amount simultáneamente. Use uno u otro."` | Ambos campos enviados |
| 400 | `base_amount` | `"Debe proporcionar base_amount o total_amount."` | Ningún monto proporcionado |
| 400 | `total_amount` | `"Debe proporcionar base_amount o total_amount."` | Ningún monto proporcionado |
| 400 | `tax_percentage` | `"La tasa de IVA debe estar entre 0 y 30%."` | IVA fuera de rango |
| 400 | `tax_percentage` | `"Para usar IVA, debe proporcionar total_amount junto con tax_percentage (modo nuevo) o base_amount junto con tax_percentage (modo tradicional)."` | IVA sin monto |
| 400 | `destination_account` | `"La cuenta destino es obligatoria para transferencias."` | Transferencia sin destino |
| 400 | `destination_account` | `"La cuenta destino debe ser diferente a la cuenta origen."` | Misma cuenta origen y destino |
| 400 | `destination_account` | `"La cuenta destino solo debe proporcionarse para transferencias."` | Destino en ingreso/gasto |
| 400 | `origin_account` | `"No se puede realizar esta transacción. El saldo resultante sería negativo (${saldo}). Saldo actual: ${actual}, Monto: ${monto}"` | Saldo insuficiente (activo) |
| 400 | `origin_account` | `"No se puede realizar esta transacción. Se excedería el límite de crédito. Límite: ${límite}, Deuda actual: ${deuda}, Crédito disponible: ${disponible}, Monto: ${monto}"` | Límite de crédito excedido |
| 400 | `origin_account` | `"Las tarjetas de crédito no pueden tener saldo positivo."` | Tarjeta con saldo positivo |
| 400 | `capital_amount` | `"El monto total es requerido cuando se especifica capital_amount."` | Capital sin total |
| 400 | `capital_amount` | `"capital_amount ({capital}) + interest_amount ({interest}) debe ser igual a total_amount ({total})."` | Suma incorrecta |
| 400 | `capital_amount` | `"El monto de capital no puede ser negativo."` | Capital negativo |
| 400 | `interest_amount` | `"El monto de intereses no puede ser negativo."` | Intereses negativos |
| 400 | `date` | `"This field is required."` | Fecha faltante |
| 400 | `date` | `"Date has wrong format. Use one of these formats instead: YYYY-MM-DD."` | Formato de fecha inválido |
| 400 | - | `"El usuario debe estar autenticado para crear una transacción."` | Usuario no autenticado |

**Ejemplo de respuesta de error:**
```json
{
  "category": ["La categoría es obligatoria para ingresos y gastos."],
  "base_amount": ["El monto base debe ser un valor positivo mayor que cero."],
  "origin_account": ["No se puede realizar esta transacción. El saldo resultante sería negativo ($-500.00). Saldo actual: $1000.00, Monto: $1500.00"]
}
```

---

### 5.4. `PATCH /api/transactions/{id}/` - Actualizar transacción

**Errores posibles:**

| Código | Campo | Mensaje | Descripción |
|--------|-------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 404 | - | `"Not found."` | Transacción no existe |
| 400 | `base_amount` | `"El monto base debe ser un valor positivo mayor que cero."` | Monto base inválido |
| 400 | `total_amount` | `"El monto total debe ser un valor positivo mayor que cero."` | Monto total inválido |
| 400 | `base_amount` | `"No se puede proporcionar base_amount y total_amount simultáneamente. Use uno u otro."` | Ambos campos enviados |
| 400 | `tax_percentage` | `"La tasa de IVA debe estar entre 0 y 30%."` | IVA fuera de rango |
| 400 | `category` | `"La categoría no pertenece al usuario autenticado."` | Categoría de otro usuario |
| 400 | `category` | `"Las transferencias no deben tener categoría asignada."` | Categoría en transferencia |
| 400 | `destination_account` | `"La cuenta destino es obligatoria para transferencias."` | Transferencia sin destino |
| 400 | `destination_account` | `"La cuenta destino debe ser diferente a la cuenta origen."` | Misma cuenta |
| 400 | `destination_account` | `"La cuenta destino solo debe proporcionarse para transferencias."` | Destino en ingreso/gasto |
| 400 | `origin_account` | `"No se puede realizar esta transacción. El saldo resultante sería negativo..."` | Saldo insuficiente |

---

### 5.5. `DELETE /api/transactions/{id}/` - Eliminar transacción

**Errores posibles:**

| Código | Mensaje | Descripción |
|--------|---------|-------------|
| 401 | - | `"Authentication credentials were not provided."` | Sin token |
| 404 | - | `"Not found."` | Transacción no existe |

---

## 📝 Notas Generales

### Códigos HTTP Comunes

- **200 OK**: Operación exitosa
- **201 Created**: Recurso creado exitosamente
- **400 Bad Request**: Error de validación o datos inválidos
- **401 Unauthorized**: Sin autenticación o token inválido
- **403 Forbidden**: Sin permisos (raro en esta API)
- **404 Not Found**: Recurso no encontrado
- **500 Internal Server Error**: Error del servidor (no debería ocurrir en producción)

### Formato de Errores

Los errores de validación vienen en formato:
```json
{
  "campo": ["mensaje de error 1", "mensaje de error 2"]
}
```

Los errores generales pueden venir como:
```json
{
  "error": "Mensaje de error",
  "detail": "Detalle adicional"
}
```

### Manejo Recomendado en Frontend

1. **Errores 401**: Redirigir al login
2. **Errores 400**: Mostrar mensajes de validación en los campos correspondientes
3. **Errores 404**: Mostrar mensaje "Recurso no encontrado"
4. **Errores 500**: Mostrar mensaje genérico de error del servidor

### Validaciones del Frontend

El frontend debe validar ANTES de enviar:
- Campos requeridos
- Formatos (email, fecha, etc.)
- Rangos numéricos
- Longitudes de texto

Esto mejora la UX, pero el backend siempre validará también.

---

**Última actualización:** 2025-01-15
**Versión del API:** 1.0

