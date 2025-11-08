from django.conf.urls.static import static
from django.urls import path

from core.solution.views.solution.views import *
from core.solution.views.solution_std.views import *
from core.solution.views.standarization.views import StandarizationSolutionCreateView
from luka import settings

app_name = 'solution'

urlpatterns = [
    path('add/', SolutionCreateView.as_view(), name='create_solution'),
    path('add_std/', SolutionStandardCreateView.as_view(), name='create_solution_std'),
    path('list/', SolutionListView.as_view(), name='list_solution'),
    path('list_std/', SolutionStdListView.as_view(), name='list_solution_std'),
    path('update/<uuid:pk>/', SolutionUpdateView.as_view(), name='update_solution'),
    path('detail/<uuid:pk>/', SolutionDetailView.as_view(), name='detail_solution'),
    path('detail_std/<uuid:pk>/', SolutionStdDetailView.as_view(), name='detail_solution_std'),
    path('add_solvent/<uuid:pk>/', SolutionAddSolventUpdateView.as_view(), name='add_solvent_solution'),
    path('add_solvent_std/<uuid:pk>/', SolutionStdAddSolventUpdateView.as_view(), name='add_solvent_solution_std'),
    path('solution_label/<uuid:pk>/', SolutionLabelPDFDetailView.as_view(), name='solution_label_pdf'),
    path('solution_label_std/<uuid:pk>/', SolutionStdLabelPDFDetailView.as_view(), name='solution_label_std_pdf'),
    path('solution_std/<uuid:pk>/', StandarizationSolutionCreateView.as_view(), name='create_solution_std'),
    path('api/inventory-reagent/<uuid:reagent_id>/', get_inventory_reagent_data, name='inventory_reagent_data'),
]

urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
