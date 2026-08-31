"""Configuración de la aplicación de condiciones ambientales."""  # noqa: E501

from django.apps import AppConfig


class ConditionConfig(AppConfig):
    """Configuración de la aplicación core.condition."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.condition'
