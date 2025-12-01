"""
Configuración de la app Analytics para HU-13
"""

from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    """
    Configuración para la aplicación de Analytics Financieros (HU-13)

    Esta app proporciona indicadores y gráficos del período con soporte
    para modo base vs total, sin requerir modelos de base de datos.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "analytics"
    verbose_name = "Analytics Financieros"

    def ready(self):
        """Configuración cuando la app está lista"""
        # No hay señales que configurar por ahora
        pass
