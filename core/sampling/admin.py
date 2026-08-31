"""Configuración del panel de administración para la aplicación sampling."""

from django.contrib import admin

from core.sampling.models import SamplingGenerationLog, SamplingGroup, SamplingProcess


class SamplingGroupAdmin(admin.ModelAdmin):
    """Administración de grupos de muestreo en el panel de Django."""

    search_fields = ('id', 'sampling_point', 'first_hour_sampling', 'number_sampling_day', 'enable_sampling_group')
    list_display = ('id', 'sampling_point', 'first_hour_sampling', 'number_sampling_day', 'enable_sampling_group')


class SamplingProcessAdmin(admin.ModelAdmin):
    """Administración de procesos de muestreo en el panel de Django."""

    search_fields = ('id', 'group_sampling', 'date_sampling_scheduled', 'date_sampling', 'number_sample',
                     'automatic_sampling', 'sampling_confirmed_by', 'sampling_created_by', 'status_sampling',
                     'batch_number')
    list_display = ('id', 'group_sampling', 'date_sampling_scheduled', 'date_sampling', 'number_sample',
                     'automatic_sampling', 'sampling_confirmed_by', 'sampling_created_by', 'status_sampling',
                     'batch_number')


class SamplingGenerationLogAdmin(admin.ModelAdmin):
    """Administración del registro de generación automática de muestras."""

    list_display = ('sampling_group', 'target_date', 'samples_created', 'skipped', 'date_creation')
    list_filter = ('skipped', 'target_date')

admin.site.register(SamplingGroup, SamplingGroupAdmin)
admin.site.register(SamplingProcess, SamplingProcessAdmin)
admin.site.register(SamplingGenerationLog, SamplingGenerationLogAdmin)
