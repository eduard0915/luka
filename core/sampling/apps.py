"""Configuración de la aplicación sampling para Django."""

from django.apps import AppConfig


class SamplingConfig(AppConfig):
    """Configuración de la aplicación de muestreo del laboratorio."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.sampling'

    def ready(self):
        """Importa las señales de la aplicación al iniciar Django."""
        try:
            import core.sampling.signals
        except ImportError as e:
            print(f"Error importing signals: {e}")
