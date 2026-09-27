"""Configuración del panel de administración para la aplicación de observaciones."""  # noqa: E501

from django.contrib import admin

from core.observation.models import Observation


class ObservationAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo Observation."""

    list_display = ('id', 'comment', 'comment_by', 'comment_date', 'sampling_process')
    list_filter = ('comment_date',)
    search_fields = ('id', 'comment', 'comment_by__username', 'sampling_process__number_sample')


admin.site.register(Observation, ObservationAdmin)
