"""Configuración de la aplicación de observaciones."""  # noqa: E501

from django.apps import AppConfig


class ObservationConfig(AppConfig):
    """Configuración de la aplicación core.observation."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.observation'
