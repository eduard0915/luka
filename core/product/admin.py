"""Configuración del administrador de Django para la aplicación product.

Registra los modelos de producto en el panel de administración e incluye
exportación/importación mediante django-import-export.
"""

from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from core.product.models import *



class ProductResource(resources.ModelResource):
    """Recurso de importación/exportación para el modelo Product."""

    class Meta:
        model = Product
        fields = ('id', 'code_product', 'description_product', 'site', 'enable_product', 'version',
                  'user_creation', 'date_creation', 'user_updated', 'date_updated')
        export_order = fields


class AnalyticalMethodProductResource(resources.ModelResource):
    """Recurso de importación/exportación para el modelo AnalyticalMethodProduct."""

    class Meta:
        model = AnalyticalMethodProduct
        fields = ('id', 'product', 'analytical_method', 'user_creation', 'date_creation', 'user_updated',
                  'date_updated')
        export_order = fields


class SpecificationProductResource(resources.ModelResource):
    """Recurso de importación/exportación para el modelo SpecificationProduct."""

    class Meta:
        model = SpecificationProduct
        fields = ('id', 'product', 'type_test', 'test_prod', 'features_prod', 'lower_limit_prod',
                  'upper_limit_prod', 'method_test', 'method_test_relacional', 'unit_measure', 'user_creation',
                  'date_creation', 'user_updated', 'date_updated')
        export_order = fields


class SamplePointResource(resources.ModelResource):
    """Recurso de importación/exportación para el modelo SamplePoint."""

    class Meta:
        model = SamplePoint
        fields = ('id', 'sample_point_code', 'sample_point_name', 'sample_frequency', 'sequence', 'product',
                  'specification', 'sample_type', 'periodicity', 'enable_point', 'user_creation', 'date_creation',
                  'user_updated', 'date_updated')
        export_order = fields


class ProductAdmin(ImportExportModelAdmin):
    """Configuración de administración para el modelo Product."""

    resource_classes = [ProductResource]
    list_display = ('id', 'code_product', 'description_product', 'site', 'version', 'enable_product')
    list_filter = ('enable_product', 'site')
    search_fields = ('id', 'code_product', 'description_product')


class AnalyticalMethodProductAdmin(ImportExportModelAdmin):
    """Configuración de administración para el modelo AnalyticalMethodProduct."""

    resource_classes = [AnalyticalMethodProductResource]
    list_display = ('id', 'product', 'analytical_method')
    list_filter = ('analytical_method', 'product')
    search_fields = ('id', 'product__description_product', 'analytical_method__description_analytical_method')


class SpecificationProductAdmin(ImportExportModelAdmin):
    """Configuración de administración para el modelo SpecificationProduct."""

    resource_classes = [SpecificationProductResource]
    list_display = ('id', 'product', 'type_test', 'test_prod', 'lower_limit_prod', 'upper_limit_prod',
                    'unit_measure', 'method_test', 'method_test_relacional')
    list_filter = ('type_test', 'product')
    search_fields = ('id', 'test_prod', 'product__description_product')


class SamplePointAdmin(ImportExportModelAdmin):
    """Configuración de administración para el modelo SamplePoint."""

    resource_classes = [SamplePointResource]
    list_display = ('id', 'sample_point_code', 'sample_point_name', 'product', 'sample_type', 'periodicity',
                    'sequence', 'sample_frequency', 'enable_point')
    list_filter = ('enable_point', 'sample_type', 'periodicity', 'product')
    search_fields = ('id', 'sample_point_code', 'sample_point_name', 'product__description_product')
    filter_horizontal = ('specification',)


admin.site.register(Product, ProductAdmin)
admin.site.register(AnalyticalMethodProduct, AnalyticalMethodProductAdmin)
admin.site.register(SpecificationProduct, SpecificationProductAdmin)
admin.site.register(SamplePoint, SamplePointAdmin)
