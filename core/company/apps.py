"""Configuración de la aplicación company (empresa, plantas y procesos)."""

from django.apps import AppConfig


class CompanyConfig(AppConfig):
    """Configuración de la aplicación de empresa para el LIMS.

    Define los metadatos de la aplicación company, incluyendo el campo
    auto incremental por defecto y la ruta del módulo.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.company'
