from django.contrib import admin

from django.contrib import admin

from core.solution.models import Solution


class SolutionAdmin(admin.ModelAdmin):
    search_fields = (
        'id', 'solute_reagent', 'solvent_reagent', 'concentration', 'concentration_unit', 'preparation_date',
        'expire_date_solution', 'quantity_solution', 'quantity_reagent', 'quantity_solvent', 'preparated_by',
        'standardizable', 'average_concentration', 'deviation_std', 'coefficient_variation'
    )
    list_display = (
        'id', 'solute_reagent', 'solvent_reagent', 'concentration', 'concentration_unit', 'preparation_date',
        'expire_date_solution', 'quantity_solution', 'quantity_reagent', 'quantity_solvent', 'preparated_by',
        'standardizable', 'average_concentration', 'deviation_std', 'coefficient_variation'
    )

admin.site.register(Solution, SolutionAdmin)
