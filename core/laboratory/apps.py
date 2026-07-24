"""Configuración de la aplicación de laboratorios."""  # noqa: E501

from django.apps import AppConfig


class LaboratoryConfig(AppConfig):
    """Configuración de la aplicación core.laboratory."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.laboratory'
