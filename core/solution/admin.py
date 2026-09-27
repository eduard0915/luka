"""Configuración del panel de administración para el módulo de soluciones."""

from django.contrib import admin

from core.solution.models import (
    Solution,
    SolutionBase,
    SolutionStd,
    SolutionStdBase,
    Standardization,
    StandardizationSolution,
    TransactionSolution,
    TransactionSolutionStd,
)


class SolutionAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo Solution."""

    search_fields = (
        'id', 'solute_reagent', 'solvent_reagent', 'concentration', 'concentration_unit', 'preparation_date',
        'expire_date_solution', 'quantity_solution', 'quantity_reagent', 'quantity_solvent', 'preparated_by',
        'standardizable', 'average_concentration', 'deviation_std', 'coefficient_variation', 'solution_base'
    )
    list_display = (
        'id', 'solute_reagent', 'solvent_reagent', 'concentration', 'concentration_unit', 'preparation_date',
        'expire_date_solution', 'quantity_solution', 'quantity_reagent', 'quantity_solvent', 'preparated_by',
        'standardizable', 'average_concentration', 'deviation_std', 'coefficient_variation', 'solution_base'
    )


class SolutionBaseAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo SolutionBase."""

    list_display = ('id', 'solute_reagent_base', 'solvent_reagent_base', 'concentration_base',
                    'concentration_unit_base', 'standardizable', 'enable_solution')
    list_filter = ('enable_solution', 'standardizable')
    search_fields = ('id', 'solute_reagent_base__description_reagent', 'solvent_reagent_base__description_reagent')


class SolutionStdBaseAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo SolutionStdBase."""

    list_display = ('id', 'solute_std_base', 'solvent_reagent_base', 'concentration_std_base',
                    'concentration_unit_base', 'standardizable', 'enable_solution_std')
    list_filter = ('enable_solution_std', 'standardizable')
    search_fields = ('id', 'solute_std_base__description_reagent',)


class SolutionStdAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo SolutionStd."""

    list_display = ('id', 'code_solution_std', 'solution_std_base', 'concentration_std', 'concentration_unit',
                    'preparation_std_date', 'expire_std_date_solution', 'quantity_available_std',
                    'preparated_std_by')
    list_filter = ('preparation_std_date', 'preparation_confirmed', 'laboratory')
    search_fields = ('id', 'code_solution_std', 'solution_std_base__solute_std_base__description_reagent')


class StandardizationAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo Standardization."""

    list_display = ('id', 'reagent_std', 'solution_base', 'solution_std_base', 'molar_relation')
    list_filter = ('solution_base', 'solution_std_base')
    search_fields = ('id', 'reagent_std__description_reagent',)


class StandardizationSolutionAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo StandardizationSolution."""

    list_display = ('id', 'solution_to_standardize', 'standard_solution', 'standard_reagent', 'quantity_standard',
                    'quantity_solution', 'concentration_sln', 'standardized_by', 'standarization_date')
    list_filter = ('standarization_date',)
    search_fields = ('id', 'standardized_by__username', 'solution_to_standardize__code_solution_std')


class TransactionSolutionAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo TransactionSolution."""

    list_display = ('id', 'solution_inventory', 'date_transaction', 'type_transaction', 'quantity',
                    'user_transaction')
    list_filter = ('type_transaction', 'date_transaction')
    search_fields = ('id', 'solution_inventory__code_solution', 'detail_transaction')


class TransactionSolutionStdAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo TransactionSolutionStd."""

    list_display = ('id', 'solution_std_inventory', 'date_transaction', 'type_transaction', 'quantity',
                    'user_transaction')
    list_filter = ('type_transaction', 'date_transaction')
    search_fields = ('id', 'solution_std_inventory__code_solution_std', 'detail_transaction')


admin.site.register(Solution, SolutionAdmin)
admin.site.register(SolutionBase, SolutionBaseAdmin)
admin.site.register(SolutionStdBase, SolutionStdBaseAdmin)
admin.site.register(SolutionStd, SolutionStdAdmin)
admin.site.register(Standardization, StandardizationAdmin)
admin.site.register(StandardizationSolution, StandardizationSolutionAdmin)
admin.site.register(TransactionSolution, TransactionSolutionAdmin)
admin.site.register(TransactionSolutionStd, TransactionSolutionStdAdmin)
