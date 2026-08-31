"""Configuración del panel de administración para la aplicación de laboratorios."""  # noqa: E501

from django.contrib import admin

from core.laboratory.models import Laboratory


class LaboratoryAdmin(admin.ModelAdmin):
    """Configuración de la vista de administración para el modelo Laboratory."""

    search_fields = ('id', 'laboratory_name', 'site', 'code_solution')
    list_display = ('id', 'laboratory_name', 'site', 'enable_laboratory')

admin.site.register(Laboratory, LaboratoryAdmin)
