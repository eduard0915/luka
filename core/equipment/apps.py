"""Configuración de la aplicación de equipos para Django."""

from django.apps import AppConfig


class EquipmentConfig(AppConfig):
    """Configuración de la aplicación de equipos del sistema Luka LIMS."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.equipment'

    def ready(self):
        """Importa las señales de la aplicación de equipos al iniciar Django."""
        try:
            import core.equipment.signals
        except ImportError as e:
            print(f"Error importing signals: {e}")
