"""
WSGI config for finanzas_back project.
"""
import os
from django.core.wsgi import get_wsgi_application

# Para producción, asegurar que use settings de producción
os.environ.setdefault('DJANGO_ENV', 'production')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finanzas_back.settings')

application = get_wsgi_application()


