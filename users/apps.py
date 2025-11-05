from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'Usuarios'
    
    def ready(self):
        # Importar signals cuando la app esté lista
        try:
            import users.signals  # noqa
        except ImportError:
            pass
