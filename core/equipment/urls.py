from django.conf.urls.static import static
from django.urls import path

from core.equipment.views.equipment_instrumental.views import *
from core.equipment.views.material_instrumental.views import *
from core.equipment.views.maintenance.views import *

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
    path('maintenance/update/<uuid:pk>/', MaintenanceUpdateView.as_view(), name='update_maintenance'),
    path('maintenance/detail/<uuid:pk>/', MaintenanceDetailView.as_view(), name='detail_maintenance'),
    path('maintenance/pdf/<uuid:pk>/', MaintenancePDFView.as_view(), name='maintenance_pdf'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
