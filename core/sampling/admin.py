"""Configuración del panel de administración para la aplicación sampling."""

from django.contrib import admin

from core.sampling.models import (
    MassiveSampleAnalysis,
    MillimoleReacted,
    SamplingAnalysis,
    SamplingAnalysisProcessing,
    SamplingAnalysisProcessingRelation,
    SamplingGenerationLog,
    SamplingGroup,
    SamplingProcess,
)


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

    list_display = ('id', 'sampling_group', 'target_date', 'samples_created', 'skipped', 'date_creation')
    list_filter = ('skipped', 'target_date')
    search_fields = ('id', 'sampling_group__sampling_point__sample_point_name', 'target_date')


class SamplingAnalysisAdmin(admin.ModelAdmin):
    """Administración de análisis de muestras en el panel de Django."""

    list_display = ('id', 'sampling_process', 'analytical_method', 'analytical_method_relation',
                    'average_concentration', 'comply', 'date_analysis', 'verified_by')
    list_filter = ('comply', 'date_analysis', 'analytical_method')
    search_fields = ('id', 'sampling_process__number_sample', 'analytical_method__description_analytical_method')


class SamplingAnalysisProcessingAdmin(admin.ModelAdmin):
    """Administración del procesamiento de análisis en el panel de Django."""

    list_display = ('id', 'sample_analysis', 'standard_solution', 'concentration_sample', 'analyzed_by',
                    'analyzed_date', 'relational_calculation')
    list_filter = ('relational_calculation', 'analyzed_date')
    search_fields = ('id', 'sample_analysis__sampling_process__number_sample',)


class SamplingAnalysisProcessingRelationAdmin(admin.ModelAdmin):
    """Administración de los cálculos relacionales del procesamiento."""

    list_display = ('id', 'sampling_analysis', 'sampling_process', 'analytical_method_calculate_relation',
                    'numerator', 'denominator', 'calcule')
    search_fields = ('id', 'sampling_analysis__sampling_process__number_sample',)


class MillimoleReactedAdmin(admin.ModelAdmin):
    """Administración del registro de milimoles reaccionados."""

    list_display = ('id', 'sampling_analysis', 'standard_solution_add', 'standard_solution_spend',
                    'milliliter_std_add', 'milliliter_std_spend', 'millimole', 'quantity_sample')
    search_fields = ('id', 'sampling_analysis__sampling_process__number_sample',)


class MassiveSampleAnalysisAdmin(admin.ModelAdmin):
    """Administración de análisis masivos de muestras."""

    list_display = ('id', 'sampling_process', 'analytical_method', 'heavy_metal', 'result', 'comply',
                    'date_analysis', 'analized_by')
    list_filter = ('comply', 'date_analysis', 'heavy_metal')
    search_fields = ('id', 'sampling_process__number_sample', 'analytical_method__description_analytical_method')


admin.site.register(SamplingGroup, SamplingGroupAdmin)
admin.site.register(SamplingProcess, SamplingProcessAdmin)
admin.site.register(SamplingGenerationLog, SamplingGenerationLogAdmin)
admin.site.register(SamplingAnalysis, SamplingAnalysisAdmin)
admin.site.register(SamplingAnalysisProcessing, SamplingAnalysisProcessingAdmin)
admin.site.register(SamplingAnalysisProcessingRelation, SamplingAnalysisProcessingRelationAdmin)
admin.site.register(MillimoleReacted, MillimoleReactedAdmin)
admin.site.register(MassiveSampleAnalysis, MassiveSampleAnalysisAdmin)
