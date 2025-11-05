"""
Configuraciones de desarrollo local
Basado en DS2 + adiciones financieras
"""

from .base import *

# Debug específico para cálculos financieros
DEBUG = True
FINANCIAL_DEBUG = True

# Base de datos local para desarrollo
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_dev.sqlite3',
    }
}

# Media files en desarrollo
MEDIA_ROOT = BASE_DIR / 'media_dev'

# CORS más permisivo en desarrollo
CORS_ALLOW_ALL_ORIGINS = True

# Debug Toolbar
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']

# Email backend para desarrollo
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Cache simple en desarrollo
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Logging menos verbose en desarrollo
LOGGING['handlers']['console']['level'] = 'INFO'
LOGGING['loggers']['django']['level'] = 'INFO'

# Configuración adicional para desarrollo
ALLOWED_HOSTS = ['*']