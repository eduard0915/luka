"""Configuración de la aplicación de inicio (home)."""  # noqa: E501

from django.apps import AppConfig


class HomeConfig(AppConfig):
    """Configuración de la aplicación core.home."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.home'
