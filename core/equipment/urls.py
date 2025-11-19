from django.conf.urls.static import static
from django.urls import path

from core.equipment.views.equipment_instrumental.views import *

from luka import settings

app_name = 'equipment'

urlpatterns = [
    # Equipos Instrumentales
    path('instrumental/add/', EquipmentInstrumentalCreateView.as_view(), name='create_equipment_instrumental'),
    path('instrumental/list/', EquipmentInstrumentalListView.as_view(), name='list_equipment_instrumental'),
    path('instrumental/update/<uuid:pk>/', EquipmentInstrumentalUpdateView.as_view(), name='update_equipment_instrumental'),
    path('instrumental/detail/<uuid:pk>/', EquipmentInstrumentalDetailView.as_view(), name='detail_equipment_instrumental'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
