"""
URL configuration for finanzas_back project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.db import connection
import django

def health_check(request):
    """Health check endpoint for deployment monitoring"""
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'django_version': django.VERSION,
            'database': 'connected',
            'timestamp': django.utils.timezone.now().isoformat() if hasattr(django.utils.timezone, 'now') else 'unknown'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'django_version': django.VERSION
        }, status=500)

def root_view(request):
    """Root endpoint"""
    return JsonResponse({
        'message': 'Finanzas Backend API',
        'status': 'running',
        'version': '1.0.0'
    })

urlpatterns = [
    path('', root_view, name='root'),
    path('health/', health_check, name='health_check'),
    path('api/', root_view, name='api_root'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/export/', include('export.urls')),
    path('api/accounts/', include('accounts.urls')),  # HU-04: Cuentas financieras
    path('api/categories/', include('categories.urls')),  # HU-05: Categorías
    path('api/budgets/', include('budgets.urls')),  # HU-07: Presupuestos por categoría
    path('api/transactions/', include('transactions.urls')),  # HU-09: Transacciones financieras
    path('api/alerts/', include('alerts.urls')),  # HU-08: Alertas de presupuestos
    path('api/goals/', include('goals.urls')),  # HU-11: Metas de ahorro
    path('api/rules/', include('rules.urls')),  # HU-12: Reglas automáticas
    path('api/analytics/', include('analytics.urls')),  # HU-13: Indicadores y gráficos del período
]

