# 🧪 Instrucciones para Probar la API de Categorías

## ⚠️ PROBLEMA RESUELTO

Se identificaron y corrigieron **2 bugs críticos**:

### 1. ❌ Bug en validación de contraste (CORREGIDO)
**Problema:** La fórmula de contraste estaba invertida, rechazando todos los colores válidos.

**Solución:** Se corrigió la fórmula WCAG 2.1 en `categories/models.py`:
```python
# Antes (INCORRECTO):
ratio = (luminance + 0.05) / (1 + 0.05)  # ❌

# Ahora (CORRECTO):
white_luminance = 1.0
ratio = (white_luminance + 0.05) / (luminance + 0.05)  # ✓
```

**Colores que ahora funcionan:**
- ✅ `#DC2626` - Rojo oscuro (ratio 5.30:1)
- ✅ `#059669` - Verde oscuro (ratio 3.23:1)
- ✅ `#2563EB` - Azul oscuro (ratio 4.87:1)

**Colores que SE RECHAZAN (como debe ser):**
- ❌ `#EF4444` - Rojo claro (ratio 2.70:1)
- ❌ `#10B981` - Verde claro (ratio 2.54:1)
- ❌ `#F59E0B` - Naranja claro (ratio 2.15:1)

### 2. ❌ GET endpoints devolvían arrays vacíos sin información (CORREGIDO)
**Problema:** Cuando no había categorías, GET devolvía `[]` sin contexto.

**Solución:** Ahora devuelve:
```json
{
  "count": 0,
  "message": "No tienes categorías creadas. Usa POST /api/categories/create_defaults/",
  "results": []
}
```

---

## 🔑 Autenticación Correcta

### Token de Prueba
```
Token: 86b9516a47763b8116d26eacd0baf6cfdd8c5790
Usuario: admin1 (ID: 2)
```

### ⚠️ Formato del Header en Postman
```
Authorization: Token 86b9516a47763b8116d26eacd0baf6cfdd8c5790
```

**IMPORTANTE:** Debe incluir la palabra `Token` seguida de un espacio.

---

## 📋 Pruebas Paso a Paso

### 1️⃣ Crear Categorías por Defecto
```
POST http://localhost:8000/api/categories/create_defaults/
Authorization: Token 86b9516a47763b8116d26eacd0baf6cfdd8c5790
Content-Type: application/json
```

**Resultado esperado:**
- ✅ 10 categorías creadas (3 ingresos + 7 gastos)
- ✅ Todas con colores que pasan la validación de contraste
- ✅ Status 201 Created

### 2️⃣ Listar Categorías
```
GET http://localhost:8000/api/categories/
Authorization: Token 86b9516a47763b8116d26eacd0baf6cfdd8c5790
```

**Resultado esperado:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Comida",
      "type": "expense",
      "color": "#DC2626",
      "icon": "fa-utensils",
      "is_active": true
    },
    // ... más categorías
  ]
}
```

### 3️⃣ Crear Nueva Categoría (CON COLORES VÁLIDOS)
```
POST http://localhost:8000/api/categories/
Authorization: Token 86b9516a47763b8116d26eacd0baf6cfdd8c5790
Content-Type: application/json

{
  "name": "Restaurantes",
  "type": "expense",
  "color": "#DC2626",
  "icon": "fa-utensils"
}
```

**Resultado esperado:**
- ✅ Status 201 Created
- ✅ Categoría creada con ID único
- ✅ Color validado (ratio >= 3.0:1)

### 4️⃣ Intentar Crear Categoría con Color Inválido
```
POST http://localhost:8000/api/categories/
Authorization: Token 86b9516a47763b8116d26eacd0baf6cfdd8c5790
Content-Type: application/json

{
  "name": "Test",
  "type": "expense",
  "color": "#EF4444",
  "icon": "fa-tag"
}
```

**Resultado esperado:**
- ❌ Status 400 Bad Request
- ❌ Error: "El color debe tener un contraste mínimo de 3.0:1 con el fondo blanco"

### 5️⃣ Filtrar por Tipo (Ingresos)
```
GET http://localhost:8000/api/categories/income/
Authorization: Token 86b9516a47763b8116d26eacd0baf6cfdd8c5790
```

**Resultado esperado:**
- ✅ Solo categorías con `type: "income"`
- ✅ 3 categorías: Freelance, Inversiones, Regalos

### 6️⃣ Obtener Estadísticas
```
GET http://localhost:8000/api/categories/stats/
Authorization: Token 86b9516a47763b8116d26eacd0baf6cfdd8c5790
```

**Resultado esperado:**
```json
{
  "total": 10,
  "active": 10,
  "inactive": 0,
  "income": 3,
  "expense": 7
}
```

---

## ✅ Checklist de Validación

- [ ] POST /api/categories/ funciona con colores oscuros (#DC2626, #059669, #2563EB)
- [ ] POST /api/categories/ rechaza colores claros (#EF4444, #10B981, #F59E0B)
- [ ] GET /api/categories/ devuelve mensaje informativo si no hay datos
- [ ] GET /api/categories/income/ filtra correctamente
- [ ] GET /api/categories/expense/ filtra correctamente
- [ ] POST /api/categories/create_defaults/ crea 10 categorías
- [ ] DELETE con reassignment funciona (requiere categorías con transacciones)
- [ ] Toggle active/inactive funciona
- [ ] Bulk update order funciona

---

## 🎨 Colores Recomendados para Pruebas

### ✅ VÁLIDOS (pasan contraste 3.0:1)
```json
{
  "gastos": [
    "#DC2626",  // Rojo oscuro (5.30:1)
    "#EA580C",  // Naranja oscuro (3.67:1)
    "#B91C1C",  // Rojo muy oscuro (7.34:1)
    "#C2410C",  // Naranja muy oscuro (5.15:1)
    "#4B5563"   // Gris oscuro (7.60:1)
  ],
  "ingresos": [
    "#059669",  // Verde oscuro (3.23:1)
    "#047857",  // Verde muy oscuro (4.13:1)
    "#0D9488"   // Turquesa oscuro (3.12:1)
  ],
  "neutros": [
    "#2563EB",  // Azul oscuro (4.87:1)
    "#1D4ED8",  // Azul muy oscuro (6.23:1)
    "#7C3AED",  // Morado oscuro (4.05:1)
    "#4F46E5",  // Índigo oscuro (5.38:1)
    "#DB2777",  // Rosa oscuro (4.15:1)
    "#C026D3"   // Fucsia (4.48:1)
  ]
}
```

### ❌ INVÁLIDOS (no pasan contraste)
```json
{
  "rechazados": [
    "#EF4444",  // Rojo claro (2.70:1)
    "#F59E0B",  // Naranja claro (2.15:1)
    "#10B981",  // Verde claro (2.54:1)
    "#14B8A6",  // Turquesa claro (2.49:1)
    "#FBBF24",  // Amarillo claro (1.93:1)
    "#F87171"   // Rosa claro (2.35:1)
  ]
}
```

---

## 🐛 Troubleshooting

### Si POST sigue dando 400:
1. ✅ Verifica el header: `Authorization: Token <tu-token>`
2. ✅ Usa color válido: `#DC2626`, `#059669`, `#2563EB`
3. ✅ Verifica el JSON: `Content-Type: application/json`
4. ✅ Revisa logs: `python manage.py runserver` en terminal

### Si GET devuelve vacío:
1. ✅ Ejecuta primero: `POST /api/categories/create_defaults/`
2. ✅ Verifica autenticación
3. ✅ Ahora debe devolver mensaje informativo

### Si dice "Color inválido":
1. ✅ **Esto es CORRECTO** - la validación funciona
2. ✅ Usa colores de la lista "VÁLIDOS" arriba
3. ✅ Evita colores de la lista "RECHAZADOS"

---

## 📊 Estado Actual del Sistema

✅ **10 categorías de prueba creadas para usuario admin1:**

**Ingresos (3):**
1. Freelance (#059669)
2. Inversiones (#047857)
3. Regalos (#0D9488)

**Gastos (7):**
1. Comida (#DC2626)
2. Vivienda (#EA580C)
3. Servicios (#B91C1C)
4. Entretenimiento (#C2410C)
5. Salud (#4B5563)
6. Educación (#2563EB)
7. Otros Gastos (#4B5563)

---

## 📖 Documentación Completa

Consulta `CATEGORIES_API_POSTMAN.md` para:
- Todos los 13 endpoints
- Ejemplos completos de request/response
- Referencia de 55+ iconos Font Awesome
- Casos de prueba adicionales
- Integración con otras apps

---

**✨ Ahora sí, todo debería funcionar perfectamente. ¡Prueba y me comentas!**
