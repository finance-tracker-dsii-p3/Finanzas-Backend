# 📋 GUÍA COMPLETA DEL BACKEND - FINANZAS BACKEND

## 🎯 **OVERVIEW DEL PROYECTO**

Este es un **backend Django REST API** para una aplicación de gestión financiera personal. Utiliza Django 4.2 con Django REST Framework para proporcionar una API robusta y escalable.

### **🏗️ ARQUITECTURA GENERAL**

```
finanzas_back/           # Proyecto Django principal
├── settings.py          # Configuración general
├── urls.py             # URLs principales
├── wsgi.py             # WSGI para producción
└── asgi.py             # ASGI para async

apps/                   # Aplicaciones Django
├── users/              # Gestión de usuarios y autenticación
├── dashboard/          # Panel principal y métricas
├── notifications/      # Sistema de notificaciones
├── reports/            # Generación de reportes
├── export/             # Exportación de datos
└── health/             # Health checks para deployment

deployment/             # Configuración de despliegue
├── .github/workflows/  # CI/CD con GitHub Actions
├── requirements.txt    # Dependencias Python
├── build.sh           # Script de build para Render
└── render.yaml        # Configuración de Render
```

---

## 🔐 **SISTEMA DE AUTENTICACIÓN Y USUARIOS**

### **Modelo de Usuario Personalizado**

```python
# users/models.py
class User(AbstractUser):
    # Campos adicionales
    identification = CharField(max_length=20, unique=True)  # Cédula/ID
    phone = CharField(max_length=15, blank=True)            # Teléfono
    role = CharField(choices=ROLE_CHOICES, default='user')  # Rol: admin/user
    is_verified = BooleanField(default=False)               # Verificado por admin
    verified_by = ForeignKey('self', null=True)             # Quién lo verificó
    verified_at = DateTimeField(null=True)                  # Cuándo fue verificado
```

### **Sistema de Roles**

- **👤 USER (user):** Usuario estándar con acceso básico
- **👨‍💼 ADMIN (admin):** Administrador con permisos elevados

### **Autenticación**

- **Token Authentication:** Usa tokens DRF para autenticación stateless
- **JWT Support:** Integración con SimpleJWT (opcional)
- **OAuth2:** Soporte para OAuth2 con django-oauth-toolkit

### **Endpoints de Usuarios**

```bash
# Autenticación básica
POST   /api/auth/register/           # Registrar nuevo usuario
POST   /api/auth/login/              # Iniciar sesión → retorna token
POST   /api/auth/logout/             # Cerrar sesión

# Gestión de perfil
GET    /api/auth/profile/            # Ver perfil actual
PUT    /api/auth/profile/update/     # Actualizar perfil
DELETE /api/auth/profile/delete/     # Eliminar propia cuenta ⭐ NUEVO
POST   /api/auth/change-password/    # Cambiar contraseña

# Panel de usuario
GET    /api/auth/dashboard/          # Dashboard personalizado

# Administración (solo admins)
GET    /api/auth/admin/users/                    # Listar usuarios
GET    /api/auth/admin/users/{id}/detail/        # Detalle de usuario
PATCH  /api/auth/admin/users/{id}/edit/          # Editar usuario completo
DELETE /api/auth/admin/users/{id}/               # Eliminar usuario
GET    /api/auth/admin/users/search/             # Buscar usuarios

# Password Reset
POST   /api/auth/password/reset-request/         # Solicitar reset
POST   /api/auth/password/reset-confirm/         # Confirmar reset
```

---

## 🎨 **ESTRUCTURA DE APLICACIONES**

### **📱 1. USERS APP - Gestión de Usuarios**

```
users/
├── models.py           # User, PasswordReset
├── serializers.py      # Validación y serialización
├── views.py           # Vistas de la API
├── urls.py            # Rutas de usuarios
├── permissions.py     # Permisos personalizados
├── managers.py        # CustomUserManager
├── services.py        # Lógica de negocio (emails, etc.)
├── signals.py         # Señales para auto-verificación
└── utils.py           # Utilidades (tokens, etc.)
```

**Características clave:**
- ✅ Registro con auto-verificación
- ✅ Sistema de tokens para reset password
- ✅ Emails automáticos con django-anymail
- ✅ Validaciones robustas con serializers

### **📊 2. DASHBOARD APP - Panel Principal**

```
dashboard/
├── models.py          # Modelos de métricas/datos
├── serializers.py     # Serialización de datos dashboard
├── views.py          # Vistas del panel
├── urls.py           # Rutas dashboard
└── services.py       # Lógica de cálculos y métricas
```

### **🔔 3. NOTIFICATIONS APP - Notificaciones**

```
notifications/
├── models.py          # Notification model
├── serializers.py     # Serialización notificaciones
├── views.py          # API de notificaciones
├── urls.py           # Rutas notificaciones
└── services.py       # Lógica de envío
```

### **📋 4. REPORTS APP - Reportes**

```
reports/
├── models.py          # Modelos de reportes
├── serializers.py     # Serialización reportes
├── views.py          # Generación de reportes
└── urls.py           # Rutas reportes
```

### **📤 5. EXPORT APP - Exportación**

```
export/
├── models.py          # Modelos de exportación
├── serializers.py     # Serialización exports
├── views.py          # Lógica de exportación
├── urls.py           # Rutas export
└── services.py       # Generación PDF/Excel
```

### **❤️ 6. HEALTH APP - Health Checks**

```
health/
├── views.py          # Health check endpoints
├── urls.py           # /health/ route
└── apps.py           # Configuración app
```

---

## ⚙️ **CONFIGURACIÓN Y SETTINGS**

### **Settings Principal**

```python
# finanzas_back/settings.py

# Base de datos
DATABASES = {
    'default': dj_database_url.parse(env('DATABASE_URL'))
}

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

# CORS (para frontend)
CORS_ALLOWED_ORIGINS = [
    env('FRONTEND_BASE_URL', default='http://localhost:3000')
]

# Email (Resend/SMTP)
EMAIL_BACKEND = 'django_anymail.backends.resend.EmailBackend'
ANYMAIL = {
    'RESEND_API_KEY': env('RESEND_API_KEY'),
}
```

### **Variables de Entorno**

```bash
# .env file structure
DATABASE_URL=postgresql://user:pass@host/db
SECRET_KEY=tu-secret-key-segura
DEBUG=False

# Email
EMAIL_HOST_USER=tu-email@dominio.com
EMAIL_HOST_PASSWORD=tu-app-password
DEFAULT_FROM_EMAIL=Soporte <soporte@dominio.com>

# URLs
FRONTEND_BASE_URL=https://tu-frontend.vercel.app
PUBLIC_BASE_URL=https://tu-backend.onrender.com

# CORS y CSRF
CORS_ALLOWED_ORIGINS=https://tu-frontend.vercel.app
CSRF_TRUSTED_ORIGINS=https://tu-backend.onrender.com
ALLOWED_HOSTS=tu-backend.onrender.com,localhost
```

---

## 🧪 **TESTING STRATEGY**

### **Estructura de Tests**

```
tests/
├── test_users_auth.py              # Tests de autenticación
├── test_users_profile.py           # Tests de perfil
├── test_delete_own_account.py      # Tests auto-eliminación ⭐ NUEVO
├── test_admin_operations.py        # Tests administración
├── test_dashboard.py               # Tests dashboard
├── test_notifications.py           # Tests notificaciones
└── test_integrations.py           # Tests integración
```

### **Comandos de Testing**

```bash
# Ejecutar todos los tests
python manage.py test

# Tests específicos
python manage.py test users.tests
python manage.py test tests.test_delete_own_account

# Con coverage
python -m pytest --cov=. --cov-report=html
```

---

## 🚀 **DEPLOYMENT Y CI/CD**

### **GitHub Actions Workflows**

```
.github/workflows/
├── ci.yml                 # Tests y validación código
├── deploy.yml             # Deployment principal
├── deploy-develop.yml     # Deployment desde develop ⭐
└── staging-deploy.yml     # Deployment staging
```

### **Render Deployment**

```yaml
# render.yaml
services:
  - type: web
    name: finanzas-backend
    env: python
    buildCommand: "./build.sh"
    startCommand: "gunicorn finanzas_back.wsgi:application --bind 0.0.0.0:$PORT --workers 3"
    healthCheckPath: "/health/"
    
databases:
  - name: finanzas-db
    databaseName: finanzas_back_db
    user: finanzas_user
```

### **Build Script**

```bash
# build.sh - Ejecutado en cada deployment
pip install -r requirements.txt
python manage.py check --deploy
python manage.py collectstatic --no-input
python manage.py migrate
```

---

## 📡 **API PATTERNS Y CONVENCIONES**

### **Response Formats**

```python
# Success Response
{
    "message": "Operación exitosa",
    "data": {...},          # Datos solicitados
    "meta": {               # Metadata (opcional)
        "pagination": {...},
        "filters": {...}
    }
}

# Error Response
{
    "error": "Descripción del error",
    "details": {...},       # Detalles específicos
    "code": "ERROR_CODE"    # Código de error (opcional)
}

# Validation Error
{
    "error": "Datos inválidos",
    "details": {
        "field_name": ["Error específico del campo"]
    }
}
```

### **HTTP Status Codes**

```python
# Éxito
200 OK           # Operación exitosa
201 CREATED      # Recurso creado
204 NO_CONTENT   # Eliminación exitosa

# Errores Cliente
400 BAD_REQUEST      # Datos inválidos
401 UNAUTHORIZED     # No autenticado
403 FORBIDDEN        # Sin permisos
404 NOT_FOUND        # Recurso no encontrado

# Errores Servidor
500 INTERNAL_ERROR   # Error interno
```

---

## 🔧 **DESARROLLO LOCAL**

### **Setup Inicial**

```bash
# 1. Clonar repositorio
git clone https://github.com/finance-tracker-dsii-p3/Finanzas-Backend.git
cd Finanzas-Backend

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar base de datos
python manage.py migrate
python manage.py createsuperuser

# 5. Ejecutar servidor
python manage.py runserver
```

### **Comandos Útiles**

```bash
# Crear migraciones
python manage.py makemigrations
python manage.py migrate

# Shell interactivo
python manage.py shell

# Recolectar archivos estáticos
python manage.py collectstatic

# Crear superusuario
python manage.py createsuperuser

# Verificar deployment
python manage.py check --deploy
```

---

## 📦 **DEPENDENCIAS PRINCIPALES**

```python
# requirements.txt estructura

# Core Django
Django==4.2.16
djangorestframework==3.14.0

# Base de datos
psycopg2-binary==2.9.11     # PostgreSQL
dj-database-url==3.0.1      # DB URL parsing

# Autenticación
djangorestframework-simplejwt==5.3.0
django-oauth-toolkit==1.7.1

# API Documentation
drf-spectacular==0.26.5     # OpenAPI/Swagger

# Email
django-anymail==10.2        # Multi-provider email

# Producción
gunicorn==21.2.0           # WSGI server
whitenoise==6.6.0          # Static files

# Utilidades
python-decouple==3.8       # Environment variables
django-cors-headers==4.3.1 # CORS handling
Pillow==10.4.0             # Image processing

# Testing
pytest==8.4.1
pytest-django==4.8.0
pytest-cov==4.1.0

# Export/Import
reportlab==4.0.9           # PDF generation
openpyxl==3.1.2           # Excel files
django-import-export==3.3.1
```

---

## 🎯 **FUNCIONALIDADES CLAVE IMPLEMENTADAS**

### ✅ **Sistema de Autenticación Completo**
- Registro con auto-verificación
- Login/Logout con tokens
- Cambio de contraseña
- Reset de contraseña via email
- **Auto-eliminación de cuenta** ⭐ NUEVO

### ✅ **Panel de Administración**
- Gestión completa de usuarios
- Verificación de usuarios
- Promoción a administrador
- Búsqueda y filtros

### ✅ **Sistema de Notificaciones**
- Notificaciones en tiempo real
- Envío de emails automático
- Gestión de estados

### ✅ **Exportación de Datos**
- Generación PDF
- Exportación Excel
- Múltiples formatos

### ✅ **CI/CD Robusto**
- Tests automáticos
- Deployment automático
- Health checks
- Múltiples entornos

---

## 🔍 **DEBUGGING Y TROUBLESHOOTING**

### **Logs y Debugging**

```python
# settings.py - Configuración de logs
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### **Problemas Comunes**

```bash
# Error de migraciones
python manage.py migrate --fake-initial
python manage.py migrate

# Error de static files
python manage.py collectstatic --clear --no-input

# Error de base de datos
python manage.py dbshell  # Acceder a DB directamente

# Error de permisos
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(username='tu_usuario')
>>> user.is_staff = True
>>> user.save()
```

---

## 📚 **RECURSOS Y DOCUMENTACIÓN**

### **Enlaces Útiles**
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Render Deployment Guide](https://render.com/docs/deploy-django)

### **API Documentation**
- **Swagger UI:** `/api/schema/swagger-ui/` (en desarrollo)
- **ReDoc:** `/api/schema/redoc/` (en desarrollo)

### **Monitoreo**
- **Health Check:** `/health/` - Estado del sistema
- **Admin Panel:** `/admin/` - Panel administrativo Django

---

## 🎉 **PRÓXIMOS PASOS RECOMENDADOS**

1. **📊 Implementar métricas de uso**
2. **🔔 Mejorar sistema de notificaciones**  
3. **📈 Agregar analytics y reporting**
4. **🔒 Implementar rate limiting**
5. **📱 Documentación API completa con Swagger**
6. **🧪 Aumentar cobertura de tests**
7. **⚡ Optimizaciones de performance**

---

**¡Esta guía te dará todo lo necesario para entender y contribuir al proyecto! 🚀**

**Para cualquier duda específica, revisa el código o ejecuta los tests relacionados.**