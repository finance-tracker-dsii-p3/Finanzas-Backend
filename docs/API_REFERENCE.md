# 📡 API REFERENCE - FINANZAS BACKEND

## 🌐 **BASE URL**

```
Development:  http://127.0.0.1:8000
Production:   https://finanzas-backend-kiq5.onrender.com
```

## 🔐 **AUTHENTICATION**

### **Token Authentication**

Todas las rutas protegidas requieren el header:

```http
Authorization: Token your-token-here
```

### **Obtener Token**

```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "tu_usuario",
  "password": "tu_contraseña"
}
```

**Response:**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": 1,
    "username": "tu_usuario",
    "email": "usuario@example.com",
    "role": "user"
  }
}
```

---

## 👤 **ENDPOINTS DE USUARIOS**

### **🔓 Registro de Usuario**

```http
POST /api/auth/register/
Content-Type: application/json
```

**Body:**
```json
{
  "username": "nuevo_usuario",
  "email": "usuario@example.com",
  "identification": "12345678",
  "password": "contraseña_segura",
  "password_confirm": "contraseña_segura",
  "phone": "+1234567890"
}
```

**Response (201 Created):**
```json
{
  "message": "Usuario registrado exitosamente",
  "user": {
    "id": 2,
    "username": "nuevo_usuario",
    "email": "usuario@example.com",
    "identification": "12345678",
    "phone": "+1234567890",
    "role": "user",
    "is_verified": true,
    "date_joined": "2025-11-11T20:30:00Z"
  },
  "token": "token-generado-automaticamente"
}
```

### **🔑 Iniciar Sesión**

```http
POST /api/auth/login/
Content-Type: application/json
```

**Body:**
```json
{
  "username": "tu_usuario",
  "password": "tu_contraseña"
}
```

**Response (200 OK):**
```json
{
  "message": "Inicio de sesión exitoso",
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": 1,
    "username": "tu_usuario",
    "email": "usuario@example.com",
    "role": "user",
    "is_verified": true
  }
}
```

### **🔒 Cerrar Sesión**

```http
POST /api/auth/logout/
Authorization: Token your-token-here
```

**Response (200 OK):**
```json
{
  "message": "Sesión cerrada exitosamente"
}
```

### **👤 Ver Perfil**

```http
GET /api/auth/profile/
Authorization: Token your-token-here
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "tu_usuario",
  "email": "usuario@example.com",
  "identification": "12345678",
  "phone": "+1234567890",
  "role": "user",
  "is_verified": true,
  "verified_at": "2025-11-11T20:30:00Z",
  "date_joined": "2025-11-10T15:20:00Z"
}
```

### **✏️ Actualizar Perfil**

```http
PUT /api/auth/profile/update/
Authorization: Token your-token-here
Content-Type: application/json
```

**Body:**
```json
{
  "email": "nuevo_email@example.com",
  "phone": "+9876543210"
}
```

**Response (200 OK):**
```json
{
  "message": "Perfil actualizado exitosamente",
  "user": {
    "id": 1,
    "username": "tu_usuario",
    "email": "nuevo_email@example.com",
    "phone": "+9876543210",
    "role": "user"
  }
}
```

### **🔒 Cambiar Contraseña**

```http
POST /api/auth/change-password/
Authorization: Token your-token-here
Content-Type: application/json
```

**Body:**
```json
{
  "current_password": "contraseña_actual",
  "new_password": "nueva_contraseña",
  "new_password_confirm": "nueva_contraseña"
}
```

**Response (200 OK):**
```json
{
  "message": "Contraseña cambiada exitosamente"
}
```

### **🗑️ Eliminar Propia Cuenta** ⭐ **NUEVO**

```http
DELETE /api/auth/profile/delete/
Authorization: Token your-token-here
Content-Type: application/json
```

**Body:**
```json
{
  "password": "mi_contraseña_actual"
}
```

**Response (200 OK):**
```json
{
  "message": "Tu cuenta ha sido eliminada exitosamente",
  "user_info": {
    "id": 1,
    "username": "usuario_eliminado",
    "email": "usuario@example.com",
    "deleted_at": "2025-11-11T20:45:00Z"
  }
}
```

**Error Responses:**
```json
// Contraseña incorrecta (400)
{
  "error": "Datos inválidos",
  "details": {
    "password": ["Contraseña incorrecta"]
  }
}

// Usuario administrador (400)
{
  "error": "Datos inválidos",
  "details": {
    "non_field_errors": ["Los administradores no pueden eliminar sus cuentas mediante este endpoint"]
  }
}
```

---

## 📊 **ENDPOINTS DE DASHBOARD**

### **📈 Dashboard Principal**

```http
GET /api/auth/dashboard/
Authorization: Token your-token-here
```

**Response (200 OK):**
```json
{
  "user": {
    "username": "tu_usuario",
    "role": "user"
  },
  "stats": {
    "total_transactions": 25,
    "total_income": 5000.00,
    "total_expenses": 3200.00,
    "balance": 1800.00
  },
  "recent_activity": [
    {
      "type": "income",
      "amount": 500.00,
      "date": "2025-11-10",
      "description": "Salary"
    }
  ]
}
```

---

## 👨‍💼 **ENDPOINTS DE ADMINISTRACIÓN**

*Requieren role="admin" o is_staff=True*

### **👥 Listar Usuarios**

```http
GET /api/auth/admin/users/
Authorization: Token admin-token-here
```

**Query Parameters:**
- `page=1` - Número de página
- `search=texto` - Buscar por username/email
- `role=user|admin` - Filtrar por rol
- `is_verified=true|false` - Filtrar por verificación

**Response (200 OK):**
```json
{
  "count": 50,
  "next": "http://127.0.0.1:8000/api/auth/admin/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "usuario1",
      "email": "user1@example.com",
      "role": "user",
      "is_verified": true,
      "date_joined": "2025-11-10T15:20:00Z"
    }
  ]
}
```

### **👤 Detalle de Usuario**

```http
GET /api/auth/admin/users/1/detail/
Authorization: Token admin-token-here
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "usuario1",
  "email": "user1@example.com",
  "identification": "12345678",
  "phone": "+1234567890",
  "role": "user",
  "is_verified": true,
  "verified_by": {
    "id": 2,
    "username": "admin_user"
  },
  "verified_at": "2025-11-10T16:00:00Z",
  "date_joined": "2025-11-10T15:20:00Z",
  "last_login": "2025-11-11T10:30:00Z"
}
```

### **✏️ Editar Usuario**

```http
PATCH /api/auth/admin/users/1/edit/
Authorization: Token admin-token-here
Content-Type: application/json
```

**Body:**
```json
{
  "role": "admin",
  "is_verified": true,
  "email": "nuevo_email@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "Usuario actualizado exitosamente",
  "user": {
    "id": 1,
    "username": "usuario1",
    "email": "nuevo_email@example.com",
    "role": "admin",
    "is_verified": true
  }
}
```

### **🗑️ Eliminar Usuario (Admin)**

```http
DELETE /api/auth/admin/users/1/
Authorization: Token admin-token-here
```

**Response (204 No Content)**

### **🔍 Buscar Usuarios**

```http
GET /api/auth/admin/users/search/?q=juan&role=user&is_verified=true
Authorization: Token admin-token-here
```

**Response (200 OK):**
```json
{
  "results": [
    {
      "id": 3,
      "username": "juan_perez",
      "email": "juan@example.com",
      "role": "user",
      "is_verified": true
    }
  ],
  "count": 1
}
```

---

## 🔒 **RESET DE CONTRASEÑA**

### **📧 Solicitar Reset**

```http
POST /api/auth/password/reset-request/
Content-Type: application/json
```

**Body:**
```json
{
  "email": "usuario@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "Si el email existe, recibirás un enlace de restablecimiento",
  "exists": true
}
```

### **✅ Confirmar Reset**

```http
POST /api/auth/password/reset-confirm/
Content-Type: application/json
```

**Body:**
```json
{
  "token": "token-recibido-por-email",
  "new_password": "nueva_contraseña_segura"
}
```

**Response (200 OK):**
```json
{
  "message": "Contraseña restablecida exitosamente"
}
```

---

## 🔔 **ENDPOINTS DE NOTIFICACIONES**

### **📜 Listar Notificaciones**

```http
GET /api/notifications/
Authorization: Token your-token-here
```

**Response (200 OK):**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "title": "Bienvenido al sistema",
      "message": "Tu cuenta ha sido verificada exitosamente",
      "type": "welcome",
      "is_read": false,
      "created_at": "2025-11-10T15:30:00Z"
    }
  ]
}
```

### **👁️ Marcar como Leída**

```http
PATCH /api/notifications/1/mark-read/
Authorization: Token your-token-here
```

**Response (200 OK):**
```json
{
  "message": "Notificación marcada como leída"
}
```

---

## 📊 **ENDPOINTS DE REPORTES**

### **📈 Generar Reporte**

```http
POST /api/reports/generate/
Authorization: Token your-token-here
Content-Type: application/json
```

**Body:**
```json
{
  "report_type": "monthly_summary",
  "date_from": "2025-11-01",
  "date_to": "2025-11-30"
}
```

**Response (200 OK):**
```json
{
  "report_id": "report_123",
  "status": "generated",
  "download_url": "/api/reports/download/report_123/"
}
```

---

## 📤 **ENDPOINTS DE EXPORTACIÓN**

### **💾 Exportar Datos**

```http
POST /api/export/
Authorization: Token your-token-here
Content-Type: application/json
```

**Body:**
```json
{
  "format": "pdf",
  "data_type": "user_profile",
  "include_transactions": true
}
```

**Response (200 OK):**
```json
{
  "export_id": "export_456",
  "status": "processing",
  "download_url": "/api/export/download/export_456/"
}
```

---

## ❤️ **HEALTH CHECK**

### **🏥 Estado del Sistema**

```http
GET /health/
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "django_version": [4, 2, 16, "final", 0],
  "database": "connected",
  "timestamp": "2025-11-11T20:50:00Z"
}
```

**Response (500 Unhealthy):**
```json
{
  "status": "unhealthy",
  "error": "Database connection failed",
  "django_version": [4, 2, 16, "final", 0]
}
```

---

## 🚨 **ERROR RESPONSES**

### **Códigos de Estado HTTP**

| Código | Descripción | Cuándo Ocurre |
|--------|-------------|---------------|
| 200 | OK | Operación exitosa |
| 201 | Created | Recurso creado exitosamente |
| 204 | No Content | Eliminación exitosa |
| 400 | Bad Request | Datos inválidos o faltantes |
| 401 | Unauthorized | Token inválido o faltante |
| 403 | Forbidden | Sin permisos para la operación |
| 404 | Not Found | Recurso no encontrado |
| 500 | Internal Error | Error interno del servidor |

### **Formato de Errores**

```json
// Error de validación (400)
{
  "error": "Datos inválidos",
  "details": {
    "email": ["Este email ya está en uso"],
    "password": ["La contraseña es muy débil"]
  }
}

// Error de autenticación (401)
{
  "detail": "Invalid token."
}

// Error de permisos (403)
{
  "detail": "You do not have permission to perform this action."
}

// Error de recurso no encontrado (404)
{
  "error": "Usuario con ID 999 no encontrado"
}

// Error interno (500)
{
  "error": "Error interno del servidor",
  "message": "Ha ocurrido un error inesperado"
}
```

---

## 📝 **EJEMPLOS DE USO CON CURL**

### **Registro y Login Completo**

```bash
# 1. Registrar usuario
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "identification": "12345678",
    "password": "secure123",
    "password_confirm": "secure123"
  }'

# 2. Login (obtener token)
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "secure123"
  }'

# 3. Ver perfil (usar token del step 2)
curl -X GET http://127.0.0.1:8000/api/auth/profile/ \
  -H "Authorization: Token your-token-here"

# 4. Eliminar cuenta
curl -X DELETE http://127.0.0.1:8000/api/auth/profile/delete/ \
  -H "Authorization: Token your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "secure123"
  }'
```

---

## 🔧 **SDK / LIBRARIES RECOMENDADAS**

### **JavaScript/TypeScript**

```javascript
// Ejemplo con Axios
const API_BASE = 'https://finanzas-backend-kiq5.onrender.com';

class FinanzasAPI {
  constructor(token = null) {
    this.token = token;
    this.client = axios.create({
      baseURL: API_BASE,
      headers: token ? { 'Authorization': `Token ${token}` } : {}
    });
  }

  async login(username, password) {
    const response = await this.client.post('/api/auth/login/', {
      username,
      password
    });
    this.token = response.data.token;
    return response.data;
  }

  async getProfile() {
    return await this.client.get('/api/auth/profile/');
  }

  async deleteAccount(password) {
    return await this.client.delete('/api/auth/profile/delete/', {
      data: { password }
    });
  }
}
```

### **Python**

```python
import requests

class FinanzasAPI:
    def __init__(self, base_url="https://finanzas-backend-kiq5.onrender.com", token=None):
        self.base_url = base_url
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers.update({'Authorization': f'Token {token}'})

    def login(self, username, password):
        response = self.session.post(f'{self.base_url}/api/auth/login/', json={
            'username': username,
            'password': password
        })
        if response.status_code == 200:
            data = response.json()
            self.token = data['token']
            self.session.headers.update({'Authorization': f'Token {self.token}'})
            return data
        response.raise_for_status()

    def get_profile(self):
        response = self.session.get(f'{self.base_url}/api/auth/profile/')
        return response.json()

    def delete_account(self, password):
        response = self.session.delete(f'{self.base_url}/api/auth/profile/delete/', json={
            'password': password
        })
        return response.json()
```

---

## 🎯 **NOTAS IMPORTANTES**

1. **🔒 Todos los tokens deben mantenerse seguros** y no exponerse en logs
2. **⏰ Los tokens no expiran automáticamente** - implementar logout manual
3. **📧 Los emails se envían automáticamente** para registro, eliminación, etc.
4. **🔄 La auto-verificación está habilitada** - usuarios se verifican automáticamente
5. **👨‍💼 Solo administradores pueden gestionar otros usuarios**
6. **🗑️ La eliminación de cuenta es irreversible** - no hay soft delete implementado

**¡Esta API reference te permitirá integrar fácilmente con el backend! 🚀**
