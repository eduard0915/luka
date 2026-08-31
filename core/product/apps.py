"""Configuración de la aplicación product para Django.

Define el nombre y la configuración predeterminada del campo
autoincremental para los modelos de la aplicación.
"""

from django.apps import AppConfig


class ProductConfig(AppConfig):
    """Configuración de la aplicación de productos del LIMS."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.product'
