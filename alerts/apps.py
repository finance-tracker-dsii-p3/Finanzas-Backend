from django.apps import AppConfig


class AlertsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "alerts"

    def ready(self):
        # Registrar señales de la app (alertas de presupuesto)
        from . import signals  # noqa: F401
