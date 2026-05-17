from django.conf.urls.static import static
from django.urls import path

from core.equipment.views.equipment_instrumental.views import *
from core.equipment.views.material_instrumental.views import *
from core.equipment.views.maintenance.views import *
from core.equipment.views.calibration.views import *
from core.equipment.views.verification.views import *
from core.equipment.views.daily_verification.views import *
from core.equipment.views.reference_pattern.views import *

from luka import settings

app_name = 'equipment'

urlpatterns = [
    # Equipos Instrumentales
    path('instrumental/add/', EquipmentInstrumentalCreateView.as_view(), name='create_equipment_instrumental'),
    path('instrumental/list/', EquipmentInstrumentalListView.as_view(), name='list_equipment_instrumental'),
    path('instrumental/update/<uuid:pk>/', EquipmentInstrumentalUpdateView.as_view(), name='update_equipment_instrumental'),
    path('instrumental/detail/<uuid:pk>/', EquipmentInstrumentalDetailView.as_view(), name='detail_equipment_instrumental'),
    path('instrumental/pdf/<uuid:pk>/', EquipmentInstrumentalPDFView.as_view(), name='equipment_instrumental_pdf'),
    # Materiales Instrumentales
    path('material/add/', MaterialInstrumentalCreateView.as_view(), name='create_material_instrumental'),
    path('material/list/', MaterialInstrumentalListView.as_view(), name='list_material_instrumental'),
    path('material/update/<uuid:pk>/', MaterialInstrumentalUpdateView.as_view(), name='update_material_instrumental'),
    path('material/detail/<uuid:pk>/', MaterialInstrumentalDetailView.as_view(), name='detail_material_instrumental'),
    # Mantenimientos
    path('maintenance/add/', MaintenanceCreateView.as_view(), name='create_maintenance'),
    path('maintenance/list/', MaintenanceListView.as_view(), name='list_maintenance'),
    path('maintenance/list_expire/', MaintenanceExpireListView.as_view(), name='list_maintenance_expire'),
    path('maintenance/update/<uuid:pk>/', MaintenanceUpdateView.as_view(), name='update_maintenance'),
    path('maintenance/detail/<uuid:pk>/', MaintenanceDetailView.as_view(), name='detail_maintenance'),
    path('maintenance/pdf/<uuid:pk>/', MaintenancePDFView.as_view(), name='maintenance_pdf'),
    # Calibraciones
    path('calibration/add/', CalibrationCreateView.as_view(), name='create_calibration'),
    path('calibration/list/', CalibrationListView.as_view(), name='list_calibration'),
    path('calibration/update/<uuid:pk>/', CalibrationUpdateView.as_view(), name='update_calibration'),
    path('calibration/detail/<uuid:pk>/', CalibrationDetailView.as_view(), name='detail_calibration'),
    path('calibration/pdf/<uuid:pk>/', CalibrationPDFView.as_view(), name='calibration_pdf'),
    # Verificaciones
    path('verification/add/', VerificationCreateView.as_view(), name='create_verification'),
    path('verification/list/', VerificationListView.as_view(), name='list_verification'),
    path('verification/update/<uuid:pk>/', VerificationUpdateView.as_view(), name='update_verification'),
    path('verification/detail/<uuid:pk>/', VerificationDetailView.as_view(), name='detail_verification'),
    path('verification/pdf/<uuid:pk>/', VerificationPDFView.as_view(), name='verification_pdf'),
    # Verificaciones Diarias
    path('daily_verification/add/', DailyVerificationCreateView.as_view(), name='create_daily_verification'),
    path('daily_verification/list/', DailyVerificationListView.as_view(), name='list_daily_verification'),
    path('daily_verification/chart/<uuid:pk>/', DailyVerificationChartView.as_view(), name='chart_daily_verification'),
    path('daily_verification/update/<uuid:pk>/', DailyVerificationUpdateView.as_view(), name='update_daily_verification'),
    path('daily_verification/detail/<uuid:pk>/', DailyVerificationDetailView.as_view(), name='detail_daily_verification'),
    path('daily_verification/pdf/<uuid:pk>/', DailyVerificationPDFView.as_view(), name='daily_verification_pdf'),
    # Patrones de Referencia
    path('reference_pattern/add/<uuid:pk>/', ReferencePatternCreateView.as_view(), name='create_reference_pattern'),
    path('reference_pattern/update/<uuid:pk>/', ReferencePatternUpdateView.as_view(), name='update_reference_pattern'),
    path('reference_pattern/delete/<uuid:pk>/', ReferencePatternDeleteView.as_view(), name='delete_reference_pattern'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
