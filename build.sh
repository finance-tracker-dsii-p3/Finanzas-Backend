#!/usr/bin/env bash
# build.sh - Script de construcción mejorado para Render

set -o errexit  # Exit en error

echo "🚀 Starting enhanced build process..."

# Update pip y instalar dependencias
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Verificar instalaciones críticas
echo "🔍 Verifying critical packages..."
python -c "
import django
try:
    import psycopg2
    print(f'✅ Django version: {django.VERSION}')
    print(f'✅ Psycopg2-binary version: {psycopg2.__version__}')
except ImportError:
    try:
        import psycopg
        print(f'✅ Django version: {django.VERSION}')
        print(f'✅ Psycopg version: {psycopg.__version__}')
    except ImportError:
        print('❌ No PostgreSQL adapter found')
        exit(1)
"

# Check de configuración Django
echo "🏗️ Checking Django configuration..."
python manage.py check --deploy

# Configurar entorno de producción
export DJANGO_ENV=production
echo "🌍 Environment set to: $DJANGO_ENV"

# Recopilar archivos estáticos
echo "📋 Collecting static files..."
python manage.py collectstatic --clear --no-input --verbosity 1

# Ejecutar migraciones
echo "🗄️ Running database migrations..."
python manage.py migrate --verbosity 1

# Crear superusuario si no existe (opcional)
echo "👤 Setting up admin user..."
if [[ $CREATE_SUPERUSER ]]; then
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', '$ADMIN_PASSWORD')
    print('✅ Superuser created')
else:
    print('✅ Superuser already exists')
"
else
    echo "🔑 Superuser creation skipped (set CREATE_SUPERUSER=1 to enable)"
fi

# Verificar que todo funcione
echo "🔍 Final health check..."
python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finanzas_back.settings')
django.setup()
print('✅ Django configuration is valid')
"

echo "✅ Build completed successfully!"