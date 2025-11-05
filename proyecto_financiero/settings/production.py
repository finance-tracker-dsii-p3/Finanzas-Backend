"""
Configuraciones de producción
Basado en DS2 + seguridad financiera
"""

from .base import *
import dj_database_url
import os

# Configuraciones financieras en producción  
FINANCIAL_DEBUG = False
DEBUG = False

# Seguridad
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Base de datos PostgreSQL en producción
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Configuración de archivos estáticos para producción
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Email en producción (configurar según proveedor)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# Validaciones estrictas para producción
FINANCIAL_SETTINGS.update({
    'STRICT_DECIMAL_VALIDATION': True,
    'LOG_FINANCIAL_OPERATIONS': True,
})

# CORS estricto en producción
CORS_ALLOW_ALL_ORIGINS = False

# Hosts permitidos desde variables de entorno
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='',
    cast=lambda v: [s.strip() for s in v.split(',')] if v else []
)

# Render.com específico
if 'RENDER_EXTERNAL_HOSTNAME' in os.environ:
    ALLOWED_HOSTS.append(config('RENDER_EXTERNAL_HOSTNAME'))

# Cache Redis en producción (opcional)
if config('REDIS_URL', default=None):
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': config('REDIS_URL'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }

# Logging para producción
LOGGING['handlers']['file']['filename'] = '/tmp/django.log'  # Render compatible