"""Configuración del panel de administración de Django para métodos analíticos.

Registra los modelos de la aplicación en el sitio de administración
para su gestión desde la interfaz de Django Admin.
"""

from django.contrib import admin

from core.analytical_method.models import (
    AnalyticalMethod,
    AnalyticalMethodCalculate,
    AnalyticalMethodCalculateRelation,
    AnalyticalMethodEquipment,
    AnalyticalMethodMaterial,
    AnalyticalMethodProcedure,
    AnalyticalMethodReagent,
    AnalyticalMethodSolution,
    AnalyticalMethodSolutionStd,
    DependentCalculation,
    GravimetryTerm,
    HeavyMetal,
    SolutionStdBackValuation,
)


class AnalyticalMethodAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo AnalyticalMethod."""

    list_display = ('id', 'code_analytical_method', 'description_analytical_method', 'type_method', 'laboratory',
                    'version', 'enable_analytical_method')
    list_filter = ('enable_analytical_method', 'type_method', 'laboratory')
    search_fields = ('id', 'code_analytical_method', 'description_analytical_method', 'type_method')


class AnalyticalMethodSolutionAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo AnalyticalMethodSolution."""

    list_display = ('id', 'analytical_method', 'solution', 'milliliter_sln')
    list_filter = ('analytical_method',)
    search_fields = ('id', 'analytical_method__description_analytical_method',
                     'solution__solute_reagent_base__description_reagent')


class AnalyticalMethodSolutionStdAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo AnalyticalMethodSolutionStd."""

    list_display = ('id', 'analytical_method', 'solution_std')
    list_filter = ('analytical_method',)
    search_fields = ('id', 'analytical_method__description_analytical_method',
                     'solution_std__solute_std_base__description_reagent')


class AnalyticalMethodReagentAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo AnalyticalMethodReagent."""

    list_display = ('id', 'analytical_method', 'reagent', 'amount_reagent')
    list_filter = ('analytical_method',)
    search_fields = ('id', 'analytical_method__description_analytical_method', 'reagent__description_reagent')


class AnalyticalMethodEquipmentAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo AnalyticalMethodEquipment."""

    list_display = ('id', 'analytical_method', 'equipment_instrumental')
    list_filter = ('analytical_method',)
    search_fields = ('id', 'analytical_method__description_analytical_method',
                     'equipment_instrumental__code_equipment')


class AnalyticalMethodMaterialAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo AnalyticalMethodMaterial."""

    list_display = ('id', 'analytical_method', 'material_instrumental')
    list_filter = ('analytical_method',)
    search_fields = ('id', 'analytical_method__description_analytical_method',
                     'material_instrumental__code_instrumental')


class AnalyticalMethodProcedureAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo AnalyticalMethodProcedure."""

    list_display = ('id', 'analytical_method', 'step_procedure', 'procedure')
    list_filter = ('analytical_method',)
    search_fields = ('id', 'analytical_method__description_analytical_method', 'procedure')


class AnalyticalMethodCalculateAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo AnalyticalMethodCalculate."""

    list_display = ('id', 'analytical_method', 'calculate_description', 'unit_measure_calculate', 'term_type',
                    'operation', 'consecutive')
    list_filter = ('term_type', 'operation', 'analytical_method')
    search_fields = ('id', 'analytical_method__description_analytical_method', 'calculate_description')


class DependentCalculationAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo DependentCalculation."""

    list_display = ('id', 'calcule_description', 'product', 'consecutive')
    list_filter = ('product',)
    search_fields = ('id', 'calcule_description', 'product__description_product')


class AnalyticalMethodCalculateRelationAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo AnalyticalMethodCalculateRelation."""

    list_display = ('id', 'calculate_description_relation', 'analytical_method', 'product', 'unit_measure_calculate',
                    'consecutive_calcule', 'operation')
    list_filter = ('operation', 'analytical_method', 'product')
    search_fields = ('id', 'calculate_description_relation', 'analytical_method__description_analytical_method',
                     'product__description_product')


class GravimetryTermAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo GravimetryTerm."""

    list_display = ('id', 'analytical_method', 'term_type', 'constant_value', 'operation', 'consecutive')
    list_filter = ('term_type', 'operation', 'analytical_method')
    search_fields = ('id', 'analytical_method__description_analytical_method',)


class SolutionStdBackValuationAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo SolutionStdBackValuation."""

    list_display = ('id', 'analytical_method', 'solution_std', 'volume_std_back')
    list_filter = ('analytical_method',)
    search_fields = ('id', 'analytical_method__description_analytical_method',
                     'solution_std__solute_std_base__description_reagent')


class HeavyMetalAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo HeavyMetal."""

    list_display = ('id', 'metal_description', 'analytical_method', 'unit_measure', 'detection_limit',
                    'quantification_limit')
    list_filter = ('analytical_method',)
    search_fields = ('id', 'metal_description', 'analytical_method__description_analytical_method')


admin.site.register(AnalyticalMethod, AnalyticalMethodAdmin)
admin.site.register(AnalyticalMethodSolution, AnalyticalMethodSolutionAdmin)
admin.site.register(AnalyticalMethodSolutionStd, AnalyticalMethodSolutionStdAdmin)
admin.site.register(AnalyticalMethodReagent, AnalyticalMethodReagentAdmin)
admin.site.register(AnalyticalMethodEquipment, AnalyticalMethodEquipmentAdmin)
admin.site.register(AnalyticalMethodMaterial, AnalyticalMethodMaterialAdmin)
admin.site.register(AnalyticalMethodProcedure, AnalyticalMethodProcedureAdmin)
admin.site.register(AnalyticalMethodCalculate, AnalyticalMethodCalculateAdmin)
admin.site.register(DependentCalculation, DependentCalculationAdmin)
admin.site.register(AnalyticalMethodCalculateRelation, AnalyticalMethodCalculateRelationAdmin)
admin.site.register(GravimetryTerm, GravimetryTermAdmin)
admin.site.register(SolutionStdBackValuation, SolutionStdBackValuationAdmin)
admin.site.register(HeavyMetal, HeavyMetalAdmin)
