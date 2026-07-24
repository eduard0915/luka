"""Configuración de la aplicación de reactivos para Django."""

from django.apps import AppConfig


class ReagentConfig(AppConfig):
    """Configuración de la aplicación core.reagent."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.reagent'

    def ready(self):
        """Registra las señales de la aplicación al iniciar Django."""
        try:
            import core.reagent.signals
        except ImportError as e:
            print(f"Error importing signals: {e}")
