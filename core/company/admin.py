"""Configuración del panel de administración de Django para la aplicación company."""

from django.contrib import admin

from core.company.models import Company, Process, Site


class CompanyAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo Company."""

    list_display = ('id', 'company_name', 'company_nit', 'company_city', 'company_country', 'autosample',
                    'service_software', 'notification_email')
    list_filter = ('autosample', 'service_software', 'notification_email')
    search_fields = ('id', 'company_name', 'company_nit')


class SiteAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo Site."""

    list_display = ('id', 'site_name', 'site_city', 'site_country', 'company', 'site_enable')
    list_filter = ('site_enable', 'company')
    search_fields = ('id', 'site_name', 'site_city', 'company__company_name')


class ProcessAdmin(admin.ModelAdmin):
    """Configuración de administración para el modelo Process."""

    list_display = ('id', 'process_name', 'site', 'enable_process')
    list_filter = ('enable_process', 'site')
    search_fields = ('id', 'process_name', 'site__site_name')


admin.site.register(Company, CompanyAdmin)
admin.site.register(Site, SiteAdmin)
admin.site.register(Process, ProcessAdmin)
