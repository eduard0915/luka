"""Configuración de la aplicación de usuarios para Django."""

from django.apps import AppConfig


class UserConfig(AppConfig):
    """Configuración de la aplicación core.user."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.user'

    def ready(self):
        """Registra las señales de la aplicación al iniciar Django."""
        try:
            import core.user.signals
        except ImportError as e:
            print(f"Error importando signals: {e}")
