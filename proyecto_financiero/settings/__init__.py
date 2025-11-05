# Importar configuración basada en environment
import os
from decouple import config

# Determinar ambiente
environment = config('DJANGO_SETTINGS_MODULE', default='proyecto_financiero.settings.development')

if 'production' in environment:
    from .production import *
elif 'testing' in environment:
    from .testing import *
else:
    from .development import *