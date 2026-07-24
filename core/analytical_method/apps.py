"""Configuración de la aplicación de métodos analíticos.

Define los metadatos y la configuración específica de la aplicación
`core.analytical_method` para Django.
"""

from django.apps import AppConfig


class AnalyticalMethodConfig(AppConfig):
    """Configuración de la aplicación de métodos analíticos.

    Establece el campo auto incremental por defecto y la ruta
    del módulo de la aplicación.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.analytical_method'
