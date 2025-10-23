from django.conf.urls.static import static
from django.urls import path

from core.reagent.views.inventory_reagent.views import *
from core.solution.views import *
from core.reagent.views.transaction_reagent.views import TransactionReagentCreateView
from luka import settings

app_name = 'solution'

urlpatterns = [
    path('add/', SolutionCreateView.as_view(), name='create_solution'),
    path('list/', SolutionListView.as_view(), name='list_solution'),
    path('update/<uuid:pk>/', SolutionUpdateView.as_view(), name='update_solution'),
    path('detail/<uuid:pk>/', SolutionDetailView.as_view(), name='detail_solution'),
    path('add_solvent/<uuid:pk>/', SolutionAddSolventUpdateView.as_view(), name='add_solvent_solution'),
    # path('inventory/register/', InventoryReagentCreateView.as_view(), name='register_inventory_reagent'),
    # path('inventory/update/<uuid:pk>/', InventoryReagentUpdateView.as_view(), name='update_inventory_reagent'),
    # path('inventory/delete/<uuid:pk>/', InventoryReagentDeleteView.as_view(), name='delete_inventory_reagent'),
    # path('inventory/list/', InventoryReagentListView.as_view(), name='list_inventory_reagent'),
    # path('transaction_reagent/add/<uuid:pk>/', TransactionReagentCreateView.as_view(), name='create_transaction_reagent'),
    # path('transaction_reagent/coa/', CertificateQualityDownloadView.as_view(), name='download_reagent_coa'),
]

urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
