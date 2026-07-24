"""Configuración de la aplicación de inicio (start)."""  # noqa: E501

from django.apps import AppConfig


class StartConfig(AppConfig):
    """Configuración de la aplicación core.start."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.start'
