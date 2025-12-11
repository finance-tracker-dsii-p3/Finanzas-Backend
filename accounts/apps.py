from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = "Cuentas Financieras"

    def ready(self):
        """Configuración cuando la app esté lista"""
        # Importar señales si las hubiera
        # import accounts.signals
