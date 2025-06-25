from django.conf.urls.static import static
from django.urls import path

from core.reagent.views.inventory_reagent.views import *
from core.reagent.views.reagent.views import *
from luka import settings

app_name = 'reagent'

urlpatterns = [
    path('add/', ReagentCreateView.as_view(), name='create_reagent'),
    path('list/', ReagentListView.as_view(), name='list_reagent'),
    path('update/<uuid:pk>/', ReagentUpdateView.as_view(), name='update_reagent'),
    path('technical_sheet/', ReagentDownloadView.as_view(), name='download_technical_sheet'),
    path('inventory/add/', InventoryReagentCreateView.as_view(), name='create_inventory_reagent'),
    path('inventory/update/<uuid:pk>/', InventoryReagentUpdateView.as_view(), name='update_inventory_reagent'),
    path('inventory/delete/<uuid:pk>/', InventoryReagentDeleteView.as_view(), name='delete_inventory_reagent'),
    path('inventory/list/', InventoryReagentListView.as_view(), name='list_inventory_reagent'),
]

urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
