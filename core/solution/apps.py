"""Configuración de la aplicación de soluciones."""

from django.apps import AppConfig


class SolutionConfig(AppConfig):
    """Configuración de la aplicación core.solution."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.solution'

    def ready(self):
        """Importa las señales del módulo de soluciones al iniciar la aplicación."""
        try:
            import core.solution.signals
        except ImportError as e:
            print(f"Error importing signals: {e}")
