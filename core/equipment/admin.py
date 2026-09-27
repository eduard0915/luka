"""Configuración del panel de administración de Django para la aplicación de equipos.

Incluye exportación/importación mediante django-import-export.
"""

from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from core.equipment.models import (
    Calibration,
    DailyVerification,
    EquipmentInstrumental,
    EquipmentUsageLog,
    Maintenance,
    MaterialInstrumental,
    ReferencePattern,
    Verification,
)


class EquipmentInstrumentalResource(resources.ModelResource):
    """Recurso de importación/exportación para el modelo EquipmentInstrumental."""

    class Meta:
        model = EquipmentInstrumental
        fields = ('id', 'code_equipment', 'description_equipment', 'supplier_equipment', 'brand_equipment',
                  'model_equipment', 'serie_equipment', 'laboratory', 'date_start_use', 'date_disabled', 'time_use',
                  'responsible_user', 'photo_equipment', 'manual_equipment', 'enable_equipment',
                  'frequency_calibration', 'frequency_maintenance', 'intermediate_verification', 'tolerance',
                  'unit_tolerance', 'date_calibration_fix', 'user_creation', 'date_creation', 'user_updated',
                  'date_updated')
        export_order = fields


class MaterialInstrumentalResource(resources.ModelResource):
    """Recurso de importación/exportación para el modelo MaterialInstrumental."""

    class Meta:
        model = MaterialInstrumental
        fields = ('id', 'code_instrumental', 'description_instrumental', 'supplier_equipment', 'brand_instrumental',
                  'date_disabled', 'responsible_user', 'photo_instrumental', 'enable_instrumental', 'user_creation',
                  'date_creation', 'user_updated', 'date_updated')
        export_order = fields


class MaintenanceResource(resources.ModelResource):
    """Recurso de importación/exportación para el modelo Maintenance."""

    class Meta:
        model = Maintenance
        fields = ('id', 'equipment_instrumental', 'date_maintenance', 'next_date_maintenance', 'type_maintenance',
                  'maintenance_by', 'description_maintenance', 'parts_change_maintenance', 'responsible_user',
                  'file_maintenance', 'maintenance_next_completed', 'user_creation', 'date_creation', 'user_updated',
                  'date_updated')
        export_order = fields


class CalibrationResource(resources.ModelResource):
    """Recurso de importación/exportación para el modelo Calibration."""

    class Meta:
        model = Calibration
        fields = ('id', 'equipment_instrumental', 'date_calibration', 'date_calibration_next', 'calibrated_by',
                  'parameter', 'observation_calibration', 'comply', 'responsible_user', 'certificate_calibration',
                  'calibration_next_completed', 'user_creation', 'date_creation', 'user_updated', 'date_updated')
        export_order = fields


class VerificationResource(resources.ModelResource):
    """Recurso de importación/exportación para el modelo Verification."""

    class Meta:
        model = Verification
        fields = ('id', 'equipment_instrumental', 'date_verification', 'date_verification_next', 'verified_by',
                  'parameter_verified', 'reference_pattern', 'observation_verification', 'comply',
                  'responsible_user', 'report_verification', 'user_creation', 'date_creation', 'user_updated',
                  'date_updated')
        export_order = fields


class ReferencePatternResource(resources.ModelResource):
    """Recurso de importación/exportación para el modelo ReferencePattern."""

    class Meta:
        model = ReferencePattern
        fields = ('id', 'equipment_instrumental', 'description_pattern', 'magnitude_pattern', 'unit_pattern',
                  'date_expire_calibration', 'certificate_calibration', 'user_creation', 'date_creation',
                  'user_updated', 'date_updated')
        export_order = fields


class DailyVerificationResource(resources.ModelResource):
    """Recurso de importación/exportación para el modelo DailyVerification."""

    class Meta:
        model = DailyVerification
        fields = ('id', 'equipment_instrumental', 'date_verification_daily', 'parameter_verified', 'reference_pattern',
                  'verification_result_daily', 'error', 'observation_verification', 'comply', 'verified_by',
                  'user_creation', 'date_creation', 'user_updated', 'date_updated')
        export_order = fields


class EquipmentUsageLogResource(resources.ModelResource):
    """Recurso de importación/exportación para el modelo EquipmentUsageLog."""

    class Meta:
        model = EquipmentUsageLog
        fields = ('id', 'equipment', 'use_date', 'sampling_analysis', 'responsible_user', 'user_creation',
                  'date_creation', 'user_updated', 'date_updated')
        export_order = fields


class EquipmentInstrumentalAdmin(ImportExportModelAdmin):
    """Configuración del administrador para el modelo EquipmentInstrumental."""

    resource_classes = [EquipmentInstrumentalResource]
    list_display = ['id', 'code_equipment', 'description_equipment', 'brand_equipment',
                    'model_equipment', 'laboratory', 'enable_equipment']
    list_filter = ['enable_equipment', 'laboratory', 'brand_equipment']
    search_fields = ['id', 'code_equipment', 'description_equipment', 'serie_equipment']


class MaterialInstrumentalAdmin(ImportExportModelAdmin):
    """Configuración del administrador para el modelo MaterialInstrumental."""

    resource_classes = [MaterialInstrumentalResource]
    list_display = ['id', 'code_instrumental', 'description_instrumental', 'brand_instrumental',
                    'responsible_user', 'enable_instrumental']
    list_filter = ['enable_instrumental', 'brand_instrumental']
    search_fields = ['id', 'code_instrumental', 'description_instrumental', 'brand_instrumental']


class MaintenanceAdmin(ImportExportModelAdmin):
    """Configuración del administrador para el modelo Maintenance."""

    resource_classes = [MaintenanceResource]
    list_display = ['id', 'equipment_instrumental', 'date_maintenance', 'next_date_maintenance', 'type_maintenance',
                    'responsible_user', 'maintenance_next_completed']
    list_filter = ['type_maintenance', 'maintenance_next_completed', 'date_maintenance']
    search_fields = ['id', 'equipment_instrumental__code_equipment', 'equipment_instrumental__description_equipment',
                     'maintenance_by']


class CalibrationAdmin(ImportExportModelAdmin):
    """Configuración del administrador para el modelo Calibration."""

    resource_classes = [CalibrationResource]
    list_display = ['id', 'equipment_instrumental', 'date_calibration', 'date_calibration_next', 'calibrated_by',
                    'comply', 'calibration_next_completed']
    list_filter = ['comply', 'calibration_next_completed', 'date_calibration']
    search_fields = ['id', 'equipment_instrumental__code_equipment', 'calibrated_by', 'parameter']


class VerificationAdmin(ImportExportModelAdmin):
    """Configuración del administrador para el modelo Verification."""

    resource_classes = [VerificationResource]
    list_display = ['id', 'equipment_instrumental', 'date_verification', 'date_verification_next', 'verified_by',
                    'comply']
    list_filter = ['comply', 'date_verification']
    search_fields = ['id', 'equipment_instrumental__code_equipment', 'verified_by', 'parameter_verified']


class ReferencePatternAdmin(ImportExportModelAdmin):
    """Configuración del administrador para el modelo ReferencePattern."""

    resource_classes = [ReferencePatternResource]
    list_display = ['id', 'description_pattern', 'equipment_instrumental', 'magnitude_pattern', 'unit_pattern',
                    'date_expire_calibration']
    list_filter = ['equipment_instrumental', 'date_expire_calibration']
    search_fields = ['id', 'description_pattern', 'equipment_instrumental__code_equipment']


class DailyVerificationAdmin(ImportExportModelAdmin):
    """Configuración del administrador para el modelo DailyVerification."""

    resource_classes = [DailyVerificationResource]
    list_display = ['id', 'equipment_instrumental', 'date_verification_daily', 'parameter_verified',
                    'reference_pattern', 'verification_result_daily', 'error', 'comply']
    list_filter = ['comply', 'date_verification_daily', 'equipment_instrumental']
    search_fields = ['id', 'equipment_instrumental__code_equipment', 'parameter_verified']


class EquipmentUsageLogAdmin(ImportExportModelAdmin):
    """Configuración del administrador para el modelo EquipmentUsageLog."""

    resource_classes = [EquipmentUsageLogResource]
    list_display = ['id', 'equipment', 'use_date', 'sampling_analysis', 'responsible_user']
    list_filter = ['use_date', 'equipment']
    search_fields = ['id', 'equipment__code_equipment', 'sampling_analysis__sampling_process__number_sample']


admin.site.register(EquipmentInstrumental, EquipmentInstrumentalAdmin)
admin.site.register(MaterialInstrumental, MaterialInstrumentalAdmin)
admin.site.register(Maintenance, MaintenanceAdmin)
admin.site.register(Calibration, CalibrationAdmin)
admin.site.register(Verification, VerificationAdmin)
admin.site.register(ReferencePattern, ReferencePatternAdmin)
admin.site.register(DailyVerification, DailyVerificationAdmin)
admin.site.register(EquipmentUsageLog, EquipmentUsageLogAdmin)
