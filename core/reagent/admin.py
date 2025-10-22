from django.contrib import admin

from core.reagent.models import Reagent


class ReagentAdmin(admin.ModelAdmin):
    search_fields = (
        'id', 'code_reagent', 'description_reagent', 'technical_sheet', 'enable_reagent', 'manufacturer', 'site', 'umb',
        'purity_unit'
    )
    list_display = (
        'id', 'code_reagent', 'description_reagent', 'technical_sheet', 'enable_reagent', 'manufacturer', 'site', 'umb',
        'purity_unit'
    )


admin.site.register(Reagent, ReagentAdmin)
