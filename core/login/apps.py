"""Configuración de la aplicación de inicio de sesión."""  # noqa: E501

from django.apps import AppConfig


class LoginConfig(AppConfig):
    """Configuración de la aplicación core.login."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.login'
