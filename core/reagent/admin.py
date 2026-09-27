"""Configuración del panel de administración de Django para la aplicación de reactivos.

Incluye exportación/importación mediante django-import-export.
"""

from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from core.reagent.models import InventoryReagent, Reagent, TransactionReagent


class ReagentResource(resources.ModelResource):
    """Recurso de importación/exportación para el modelo Reagent."""

    class Meta:
        model = Reagent
        fields = ('id', 'code_reagent', 'description_reagent', 'technical_sheet', 'enable_reagent', 'manufacturer',
                  'site', 'umb', 'purity_unit', 'molecular_weight', 'gram_equivalent', 'volumetric', 'solvent',
                  'density_enable', 'sig_figs_solution', 'standard', 'ready_to_use', 'user_creation', 'date_creation',
                  'user_updated', 'date_updated')
        export_order = fields


class InventoryReagentResource(resources.ModelResource):
    """Recurso de importación/exportación para el modelo InventoryReagent."""

    class Meta:
        model = InventoryReagent
        fields = ('id', 'reagent', 'batch_number', 'date_expire', 'quantity_stock', 'purity',
                  'certificate_quality', 'density', 'user_creation', 'date_creation', 'user_updated', 'date_updated')
        export_order = fields


class TransactionReagentResource(resources.ModelResource):
    """Recurso de importación/exportación para el modelo TransactionReagent."""

    class Meta:
        model = TransactionReagent
        fields = ('id', 'reagent_inventory', 'date_transaction', 'type_transaction', 'detail_transaction',
                  'quantity', 'user_transaction', 'sampling_analysis', 'user_creation', 'date_creation',
                  'user_updated', 'date_updated')
        export_order = fields


class ReagentAdmin(ImportExportModelAdmin):
    """Configuración de administración para el modelo Reagent."""

    resource_classes = [ReagentResource]
    search_fields = (
        'id', 'code_reagent', 'description_reagent', 'technical_sheet', 'enable_reagent', 'manufacturer', 'site', 'umb',
        'purity_unit'
    )
    list_display = (
        'id', 'code_reagent', 'description_reagent', 'technical_sheet', 'enable_reagent', 'manufacturer', 'site', 'umb',
        'purity_unit'
    )


class InventoryReagentAdmin(ImportExportModelAdmin):
    """Configuración de administración para el modelo InventoryReagent."""

    resource_classes = [InventoryReagentResource]
    list_display = ('id', 'reagent', 'batch_number', 'date_expire', 'quantity_stock', 'purity', 'density')
    list_filter = ('date_expire', 'reagent')
    search_fields = ('id', 'reagent__code_reagent', 'reagent__description_reagent', 'batch_number')


class TransactionReagentAdmin(ImportExportModelAdmin):
    """Configuración de administración para el modelo TransactionReagent."""

    resource_classes = [TransactionReagentResource]
    list_display = ('id', 'reagent_inventory', 'date_transaction', 'type_transaction', 'quantity',
                    'user_transaction')
    list_filter = ('type_transaction', 'date_transaction')
    search_fields = ('id', 'reagent_inventory__reagent__description_reagent', 'detail_transaction')


admin.site.register(Reagent, ReagentAdmin)
admin.site.register(InventoryReagent, InventoryReagentAdmin)
admin.site.register(TransactionReagent, TransactionReagentAdmin)
