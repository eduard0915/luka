from django.conf.urls.static import static
from django.urls import path

from core.reagent.views.inventory_reagent.views import *
from core.reagent.views.reagent.views import *
from core.reagent.views.transaction_reagent.views import TransactionReagentCreateView
from luka import settings

app_name = 'reagent'

urlpatterns = [
    path('add/', ReagentCreateView.as_view(), name='create_reagent'),
    path('list/', ReagentListView.as_view(), name='list_reagent'),
    path('update/<uuid:pk>/', ReagentUpdateView.as_view(), name='update_reagent'),
    path('technical_sheet/', ReagentDownloadView.as_view(), name='download_technical_sheet'),
    path('inventory/register/', InventoryReagentCreateView.as_view(), name='register_inventory_reagent'),
    path('inventory/update/<uuid:pk>/', InventoryReagentUpdateView.as_view(), name='update_inventory_reagent'),
    path('inventory/delete/<uuid:pk>/', InventoryReagentDeleteView.as_view(), name='delete_inventory_reagent'),
    path('inventory/list/', InventoryReagentListView.as_view(), name='list_inventory_reagent'),
    path('inventory/detail/<uuid:pk>/', InventoryReagentDetailView.as_view(), name='detail_inventory_reagent'),
    path('transaction_reagent/add/<uuid:pk>/', TransactionReagentCreateView.as_view(), name='create_transaction_reagent'),
    path('transaction_reagent/coa/', CertificateQualityDownloadView.as_view(), name='download_reagent_coa'),
]

urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
