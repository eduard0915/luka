"""Configuración de la aplicación report para Django."""

from django.apps import AppConfig


class ReportConfig(AppConfig):
    """Configuración de la aplicación de reportes del laboratorio."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core.report'
