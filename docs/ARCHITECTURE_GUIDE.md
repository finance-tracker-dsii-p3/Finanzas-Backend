# 🏗️ ARQUITECTURA Y PATRONES DE CÓDIGO - FINANZAS BACKEND

## 🎯 **FILOSOFÍA DE DESARROLLO**

Este proyecto sigue principios de **Clean Architecture** y **Domain-Driven Design (DDD)** adaptados para Django, priorizando:

- **Separación de responsabilidades** clara entre capas
- **Código testeable** y mantenible
- **APIs RESTful** consistentes
- **Seguridad por diseño**
- **Escalabilidad horizontal**

---

## 🔧 **ESTRUCTURA DE CAPAS**

```
┌─────────────────────────────────────────────┐
│                 API LAYER                   │  ← URLs, Views, Serializers
├─────────────────────────────────────────────┤
│               SERVICE LAYER                 │  ← Lógica de negocio
├─────────────────────────────────────────────┤
│               DOMAIN LAYER                  │  ← Models, Permissions
├─────────────────────────────────────────────┤
│            INFRASTRUCTURE LAYER             │  ← Email, Storage, External APIs
└─────────────────────────────────────────────┘
```

### **📝 1. API Layer - Capa de Presentación**

```python
# views.py - Responsabilidad: Manejar requests HTTP
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_own_account_view(request):
    """
    Solo maneja la entrada/salida HTTP.
    Delega la lógica al serializer y service.
    """
    serializer = DeleteOwnAccountSerializer(data=request.data)
    if serializer.is_valid():
        # Delegar al service layer
        result = UserService.delete_user_account(request.user)
        return Response(result, status=200)
    return Response(serializer.errors, status=400)

# serializers.py - Responsabilidad: Validación y transformación
class DeleteOwnAccountSerializer(serializers.Serializer):
    """
    Solo valida datos de entrada.
    No contiene lógica de negocio.
    """
    password = serializers.CharField(required=True)
    
    def validate_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise ValidationError("Contraseña incorrecta")
        return value
```

### **🔄 2. Service Layer - Lógica de Negocio**

```python
# services.py - Responsabilidad: Coordinar operaciones complejas
class UserService:
    @staticmethod
    def delete_user_account(user):
        """
        Orquesta el proceso completo de eliminación.
        Coordina múltiples operaciones manteniendo consistencia.
        """
        with transaction.atomic():
            # 1. Guardar info para auditoría
            user_info = UserService._prepare_deletion_info(user)
            
            # 2. Revocar tokens activos
            UserService._revoke_user_tokens(user)
            
            # 3. Notificar eliminación
            NotificationService.send_account_deleted_notification(user)
            
            # 4. Eliminar usuario (dispara señales)
            user.delete()
            
            return {
                'message': 'Cuenta eliminada exitosamente',
                'user_info': user_info
            }
    
    @staticmethod
    def _prepare_deletion_info(user):
        """Helper privado para preparar info de eliminación"""
        return {
            'username': user.username,
            'email': user.email,
            'deleted_at': timezone.now().isoformat()
        }
```

### **📊 3. Domain Layer - Modelos de Dominio**

```python
# models.py - Responsabilidad: Entidades de dominio y reglas de negocio
class User(AbstractUser):
    """
    Entidad principal del dominio de usuarios.
    Contiene reglas de negocio fundamentales.
    """
    
    def can_delete_own_account(self):
        """Regla de negocio: quién puede eliminar su cuenta"""
        return not (self.is_staff or self.is_superuser)
    
    def has_pending_transactions(self):
        """Regla de negocio: verificar transacciones pendientes"""
        # Lógica específica del dominio financiero
        return False
    
    class Meta:
        # Constraints de dominio
        constraints = [
            models.UniqueConstraint(
                fields=['email'], 
                name='unique_email'
            )
        ]

# permissions.py - Responsabilidad: Reglas de autorización
class IsAccountOwner(BasePermission):
    """
    Permiso de dominio: solo el dueño puede acceder a su cuenta
    """
    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id
```

### **🌐 4. Infrastructure Layer - Servicios Externos**

```python
# services/email_service.py
class EmailService:
    """
    Abstrae el envío de emails de la implementación específica.
    Permite cambiar providers sin afectar lógica de negocio.
    """
    
    @staticmethod
    def send_account_deleted_email(user):
        EmailAdapter.send_template_email(
            template='account_deleted',
            to=user.email,
            context={'username': user.username}
        )

# adapters/email_adapter.py  
class EmailAdapter:
    """Adapter pattern para diferentes proveedores de email"""
    
    @staticmethod
    def send_template_email(template, to, context):
        if settings.EMAIL_PROVIDER == 'resend':
            return ResendProvider.send(template, to, context)
        elif settings.EMAIL_PROVIDER == 'sendgrid':
            return SendGridProvider.send(template, to, context)
```

---

## 🎨 **PATRONES DE DISEÑO IMPLEMENTADOS**

### **🏭 1. Factory Pattern - Creación de Usuarios**

```python
# managers.py
class CustomUserManager(BaseUserManager):
    """
    Factory para crear diferentes tipos de usuarios.
    Centraliza la lógica de creación.
    """
    
    def create_user(self, email, identification, password=None, **extra_fields):
        """Factory method para usuarios normales"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('role', User.USER)
        
        return self._create_user(email, identification, password, **extra_fields)
    
    def create_superuser(self, email, identification, password=None, **extra_fields):
        """Factory method para superusuarios"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.ADMIN)
        
        return self._create_user(email, identification, password, **extra_fields)
```

### **📡 2. Observer Pattern - Señales Django**

```python
# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=User)
def auto_verify_new_users(sender, instance, created, **kwargs):
    """
    Observer que reacciona a la creación de usuarios.
    Desacopla la auto-verificación del proceso de creación.
    """
    if created and not instance.is_verified:
        instance.is_verified = True
        instance.verified_at = timezone.now()
        instance.save(update_fields=['is_verified', 'verified_at'])

@receiver(post_delete, sender=User)
def send_deletion_notification(sender, instance, **kwargs):
    """
    Observer que reacciona a la eliminación de usuarios.
    Envía notificaciones automáticamente.
    """
    EmailService.send_account_deleted_email(instance)
```

### **🎯 3. Strategy Pattern - Validaciones**

```python
# validators.py
class PasswordValidator:
    """Strategy pattern para diferentes tipos de validación"""
    
    @staticmethod
    def validate_strength(password):
        strategies = [
            LengthValidator(),
            ComplexityValidator(), 
            CommonPasswordValidator()
        ]
        
        for strategy in strategies:
            strategy.validate(password)

class LengthValidator:
    def validate(self, password):
        if len(password) < 8:
            raise ValidationError("Mínimo 8 caracteres")

class ComplexityValidator:
    def validate(self, password):
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Debe contener mayúsculas")
```

### **🔧 4. Adapter Pattern - Múltiples Providers**

```python
# adapters/storage_adapter.py
class StorageAdapter:
    """
    Adapta diferentes servicios de almacenamiento.
    Permite cambiar entre local, S3, etc.
    """
    
    @staticmethod
    def save_file(file, path):
        if settings.STORAGE_PROVIDER == 'local':
            return LocalStorageProvider.save(file, path)
        elif settings.STORAGE_PROVIDER == 's3':
            return S3StorageProvider.save(file, path)
```

---

## 📋 **CONVENCIONES DE CÓDIGO**

### **🏷️ 1. Naming Conventions**

```python
# Classes - PascalCase
class UserRegistrationSerializer(serializers.ModelSerializer):
    pass

# Functions/Methods - snake_case
def delete_own_account_view(request):
    pass

# Variables - snake_case
user_profile_data = {}

# Constants - SCREAMING_SNAKE_CASE
MAX_LOGIN_ATTEMPTS = 5

# URLs - kebab-case
path('profile/delete/', views.delete_own_account_view, name='delete_own_account')
```

### **📝 2. Documentation Standards**

```python
def complex_business_method(user_id, action_type):
    """
    Descripción clara de qué hace el método.
    
    Args:
        user_id (int): ID del usuario a procesar
        action_type (str): Tipo de acción ('create', 'update', 'delete')
    
    Returns:
        dict: Resultado de la operación con estructura:
            {
                'success': bool,
                'message': str,
                'data': dict
            }
    
    Raises:
        ValidationError: Si los datos son inválidos
        PermissionError: Si el usuario no tiene permisos
    
    Example:
        >>> result = complex_business_method(1, 'create')
        >>> print(result['success'])
        True
    """
    pass
```

### **🧪 3. Testing Patterns**

```python
# tests/test_user_deletion.py
class DeleteOwnAccountTestCase(TestCase):
    """
    Tests organizados por funcionalidad.
    Cada test verifica UN comportamiento específico.
    """
    
    def setUp(self):
        """Setup común para todos los tests"""
        self.user = self._create_test_user()
        self.client = APIClient()
    
    def test_delete_own_account_success(self):
        """Test del caso feliz - eliminación exitosa"""
        # Given - Preparar datos
        self.client.force_authenticate(user=self.user)
        data = {'password': 'correct_password'}
        
        # When - Ejecutar acción
        response = self.client.delete('/api/auth/profile/delete/', data)
        
        # Then - Verificar resultado
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(id=self.user.id).exists())
    
    def _create_test_user(self):
        """Helper para crear usuarios de test"""
        return User.objects.create_user(
            username='testuser',
            email='test@example.com',
            identification='12345678',
            password='testpass123'
        )
```

---

## 🔒 **SECURITY PATTERNS**

### **🛡️ 1. Validation Layers**

```python
# Múltiples capas de validación
class SecureView:
    """
    1. Authentication - ¿Quién eres?
    2. Permission - ¿Puedes hacer esto?
    3. Validation - ¿Los datos son válidos?
    4. Business Rules - ¿Es permitido por las reglas de negocio?
    """
    
    @authentication_classes([TokenAuthentication])  # Capa 1
    @permission_classes([IsAuthenticated])          # Capa 2
    def post(self, request):
        serializer = SecureSerializer(data=request.data)  # Capa 3
        
        if serializer.is_valid():
            # Capa 4 - Reglas de negocio
            if not BusinessRules.can_perform_action(request.user):
                return Response({'error': 'Action not allowed'}, 403)
            
            # Ejecutar acción
            return self.perform_action(serializer.validated_data)
```

### **🔐 2. Token Security**

```python
# utils/security.py
class TokenSecurity:
    """
    Manejo seguro de tokens y contraseñas.
    Nunca almacenar tokens en logs o respuestas.
    """
    
    @staticmethod
    def generate_secure_token():
        """Genera tokens criptográficamente seguros"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def hash_sensitive_data(data):
        """Hashea datos sensibles antes de almacenar"""
        salt = secrets.token_hex(16)
        return hashlib.pbkdf2_hmac('sha256', data.encode(), salt.encode(), 100000)
```

---

## ⚡ **PERFORMANCE PATTERNS**

### **🗃️ 1. Database Optimization**

```python
# Optimized queries
class OptimizedUserService:
    
    @staticmethod
    def get_users_with_profiles():
        """
        Usa select_related para evitar N+1 queries.
        Prefetch para relaciones many-to-many.
        """
        return User.objects.select_related('profile')\
                          .prefetch_related('notifications')\
                          .filter(is_active=True)
    
    @staticmethod
    def bulk_update_users(user_updates):
        """Bulk operations para operaciones masivas"""
        User.objects.bulk_update(
            user_updates, 
            ['is_verified', 'verified_at']
        )
```

### **📊 2. Caching Strategy**

```python
# services/cache_service.py
from django.core.cache import cache

class CacheService:
    """
    Estrategia de cache por capas.
    Cache de consultas frecuentes y datos estáticos.
    """
    
    @staticmethod
    def get_user_dashboard_data(user_id):
        cache_key = f'dashboard_data_{user_id}'
        data = cache.get(cache_key)
        
        if data is None:
            data = DashboardService.calculate_user_data(user_id)
            cache.set(cache_key, data, timeout=300)  # 5 minutos
        
        return data
```

---

## 📈 **MONITORING Y OBSERVABILITY**

### **📊 1. Logging Strategy**

```python
# utils/logging.py
import logging

logger = logging.getLogger(__name__)

class BusinessLogger:
    """
    Logging estructurado para operaciones de negocio.
    Facilita debugging y monitoreo.
    """
    
    @staticmethod
    def log_user_action(user, action, details=None):
        logger.info(
            f"User action performed",
            extra={
                'user_id': user.id,
                'action': action,
                'details': details,
                'timestamp': timezone.now().isoformat()
            }
        )
    
    @staticmethod
    def log_security_event(event_type, user=None, details=None):
        logger.warning(
            f"Security event: {event_type}",
            extra={
                'event_type': event_type,
                'user_id': user.id if user else None,
                'details': details,
                'ip_address': details.get('ip') if details else None
            }
        )
```

### **📍 2. Health Monitoring**

```python
# health/views.py
class HealthCheckView:
    """
    Health checks comprehensivos para monitoreo.
    Verifica todos los componentes críticos.
    """
    
    def get(self, request):
        health_status = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'checks': {
                'database': self._check_database(),
                'cache': self._check_cache(),
                'email': self._check_email_service(),
                'storage': self._check_storage(),
            }
        }
        
        # Si algún check falla, status general = unhealthy
        if any(not check['healthy'] for check in health_status['checks'].values()):
            health_status['status'] = 'unhealthy'
            return Response(health_status, status=503)
        
        return Response(health_status, status=200)
```

---

## 🎯 **BEST PRACTICES RESUMIDAS**

### ✅ **DO - Haz Esto**

```python
# ✅ Separar responsabilidades claramente
# ✅ Usar type hints
def process_user_data(user_id: int, data: dict) -> dict:
    pass

# ✅ Validar en múltiples capas
# ✅ Manejar errores específicamente
try:
    user = User.objects.get(id=user_id)
except User.DoesNotExist:
    logger.warning(f"User {user_id} not found")
    return {'error': 'User not found'}

# ✅ Usar constantes para valores mágicos
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# ✅ Tests descriptivos
def test_user_cannot_delete_account_with_wrong_password(self):
    pass
```

### ❌ **DON'T - Evita Esto**

```python
# ❌ Lógica de negocio en views
def some_view(request):
    # NO hacer cálculos complejos aquí
    complex_calculation = user.income * 0.15  # ❌
    
# ❌ Queries N+1
for user in User.objects.all():  # ❌
    print(user.profile.name)  # Query por cada user

# ❌ Hardcoded values
if user.role == 'admin':  # ❌ Usar User.ADMIN
    pass

# ❌ Excesiva complejidad en un método
def god_method(self):  # ❌ Dividir en métodos más pequeños
    # 100+ líneas de código
    pass
```

---

## 🎨 **CONCLUSIÓN**

Esta arquitectura te proporciona:

- **🔧 Mantenibilidad:** Código fácil de entender y modificar
- **🧪 Testabilidad:** Cada componente se puede testear independientemente  
- **📈 Escalabilidad:** Fácil agregar nuevas funcionalidades
- **🔒 Seguridad:** Múltiples capas de validación y autorización
- **⚡ Performance:** Optimizaciones en queries y cache
- **🔍 Observability:** Logging y monitoring comprehensivo

**Sigue estos patrones y tu código será robusto, mantenible y escalable! 🚀**