from django.contrib import admin

from core.equipment.models import EquipmentInstrumental


class EquipmentInstrumentalAdmin(admin.ModelAdmin):
    list_display = ['code_equipment', 'description_equipment', 'brand_equipment',
                    'model_equipment', 'laboratory', 'enable_equipment']
    list_filter = ['enable_equipment', 'laboratory', 'brand_equipment']
    search_fields = ['code_equipment', 'description_equipment', 'serie_equipment']


admin.site.register(EquipmentInstrumental, EquipmentInstrumentalAdmin)
