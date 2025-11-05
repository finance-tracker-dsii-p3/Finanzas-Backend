"""
Configuraciones para tests
Basado en DS2 + tests financieros
"""

from .base import *

# Base de datos en memoria para tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Archivos de test
MEDIA_ROOT = BASE_DIR / 'test_media'
DEFAULT_FILE_STORAGE = 'django.core.files.storage.InMemoryStorage'

# Email para tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Cache simple para tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Passwords simples para tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Configuraciones específicas para tests financieros
FINANCIAL_SETTINGS.update({
    'TEST_MODE': True,
    'STRICT_DECIMAL_VALIDATION': False,  # Más flexible en tests
    'LOG_FINANCIAL_OPERATIONS': False,   # No logs en tests
})

# Desactivar migraciones en tests para velocidad
class DisableMigrations:
    def __contains__(self, item):
        return True
        
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Logging mínimo en tests - solo consola
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'WARNING',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Debug False en tests
DEBUG = False
FINANCIAL_DEBUG = False