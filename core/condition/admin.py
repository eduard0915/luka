"""Configuración del panel de administración para la aplicación de condiciones ambientales."""  # noqa: E501

from django.contrib import admin

from core.condition.models import Condition, ConditionRegister


class ConditionAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo Condition."""

    list_display = ('id', 'area', 'variable', 'lower_limit', 'upper_limit', 'laboratory', 'enabled')
    list_filter = ('enabled', 'laboratory', 'area')
    search_fields = ('id', 'area', 'variable')


class ConditionRegisterAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo ConditionRegister."""

    list_display = ('id', 'condition', 'registration_date', 'registered_data', 'registered_by',
                    'actions_registered_by')
    list_filter = ('registration_date', 'condition')
    search_fields = ('id', 'condition__area', 'condition__variable', 'registered_by__username')


admin.site.register(Condition, ConditionAdmin)
admin.site.register(ConditionRegister, ConditionRegisterAdmin)
