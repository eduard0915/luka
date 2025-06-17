from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from core.company.views.company.views import *
from core.company.views.site.views import *

app_name = 'company'

urlpatterns = [
    # Company
    path('add/', CompanyCreateView.as_view(), name='company_create'),
    path('update/<uuid:pk>/', CompanyUpdateView.as_view(), name='company_update'),
    path('detail/<uuid:pk>/', CompanyDetailView.as_view(), name='company_detail'),
    # Plantas
    path('add_site/', SiteCreateView.as_view(), name='create_site'),
    path('update_site/<uuid:pk>/', SiteUpdateView.as_view(), name='update_site'),
    path('detail_site/<uuid:pk>/', SiteDetailView.as_view(), name='detail_site'),
    path('list_site/', SiteListView.as_view(), name='list_site'),
    # # Limpieza
    # path('add_sanitizer/', SanitizerCreateView.as_view(), name='sanitizer_create'),
    # path('update_sanitizer/<uuid:pk>/', SanitizerUpdateView.as_view(), name='sanitizer_update'),
    # path('list_sanitizer/', SanitizerListView.as_view(), name='sanitizer_list'),
    # # Código QR
    # path('qr_create/', GeneratorQRCreateView.as_view(), name='qr_create'),
    # path('qr_list/', GeneratorQRListView.as_view(), name='qr_list'),
    # path('qr_update/<int:pk>/', GeneratorQRUpdateView.as_view(), name='qr_update'),
    # path('qr_delete/<int:pk>/', GeneratorQRDeleteView.as_view(), name='qr_delete'),
    # path('qr/<int:pk>/', GeneratorQRPdf.as_view(), name='qr_pdf'),
    # # Formatos
    # path('add_format/', FormatCreateView.as_view(), name='format_create'),
    # path('update_format/<uuid:pk>/', FormatUpdateView.as_view(), name='format_update'),
    # path('disable_format/<uuid:pk>/', FormatDisableUpdateView.as_view(), name='format_disable'),
    # path('enable_format/<uuid:pk>/', FormatEnableUpdateView.as_view(), name='format_enable'),
    # path('list_format/', FormatListView.as_view(), name='format_list'),
    # # Defectos
    # path('add_defect/', DefectCreateView.as_view(), name='defect_create'),
    # path('update_defect/<uuid:pk>/', DefectUpdateView.as_view(), name='defect_update'),
    # path('list_defect/', DefectListView.as_view(), name='defect_list'),
    # # Equipo de Producción
    # path('list_production_equipment/', ProductionEquipmentListView.as_view(), name='production_equipment_list'),
    # path('create_production_equipment/', ProductionEquipmentCreateView.as_view(), name='production_equipment_create'),
    # path('update_production_equipment/<uuid:pk>/', ProductionEquipmentUpdateView.as_view(),
    #      name='production_equipment_update'),
    # # vsc
    # path('list_report_vsc/', ReportListViewView.as_view(), name='report_list_vsc'),
    # path('report_vsc_dq/', ValidationSystemComputerDQListView.as_view(), name='report_vsc_dq'),
    # path('report_vsc_iq/', ValidationSystemComputerIQListView.as_view(), name='report_vsc_iq'),
    # path('report_vsc_oq/', ValidationSystemComputerOQListView.as_view(), name='report_vsc_oq'),
    # path('report_vsc_pq/', ValidationSystemComputerPQListView.as_view(), name='report_vsc_pq'),
    # path('report_vsc_download/', ValidationSystemComputerDownloadView.as_view(), name='report_vsc_download'),
    # path('report_vsc_pdf_viewer/', PdfView.as_view(), name='report_vsc_pdf_viewer'),
]

urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
