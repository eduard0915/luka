from django.conf.urls.static import static
from django.urls import path

from core.solution.views.solution.views import *
from core.solution.views.solution_base.views import *
from core.solution.views.solution_stb_base.views import *
from core.solution.views.solution_std.views import *
from core.solution.views.standardization_sln.views import *
from core.solution.views.standarization.views import StandardizationCreateView, StandardizationUpdateView

from luka import settings

app_name = 'solution'

urlpatterns = [
    path('add/', SolutionCreateView.as_view(), name='create_solution'),
    path('add_base/', SolutionBaseCreateView.as_view(), name='create_solution_base'),
    path('add_std_base/', SolutionStdBaseCreateView.as_view(), name='create_solution_std_base'),
    path('add_std/', SolutionStandardCreateView.as_view(), name='create_solution_std'),
    path('list/', SolutionListView.as_view(), name='list_solution'),
    path('list_base/', SolutionBaseListView.as_view(), name='list_solution_base'),
    path('list_std_base/', SolutionStdBaseListView.as_view(), name='list_solution_std_base'),
    path('list_std/', SolutionStdListView.as_view(), name='list_solution_std'),
    path('update/<uuid:pk>/', SolutionUpdateView.as_view(), name='update_solution'),
    path('update_base/<uuid:pk>/', SolutionBaseUpdateView.as_view(), name='update_solution_base'),
    path('update_std_base/<uuid:pk>/', SolutionStdBaseUpdateView.as_view(), name='update_solution_std_base'),
    path('detail/<uuid:pk>/', SolutionDetailView.as_view(), name='detail_solution'),
    path('detail_std/<uuid:pk>/', SolutionStdDetailView.as_view(), name='detail_solution_std'),
    path('confirmed/<uuid:pk>/', SolutionConfirmedUpdateView.as_view(), name='confirmed_solution'),
    path('confirmed_std/<uuid:pk>/', SolutionStdConfirmedUpdateView.as_view(), name='confirmed_solution_std'),
    path('solution_label/<uuid:pk>/', SolutionLabelPDFDetailView.as_view(), name='solution_label_pdf'),
    path('solution_label_std/<uuid:pk>/', SolutionStdLabelPDFDetailView.as_view(), name='solution_label_std_pdf'),
    path('api/inventory-reagent/<uuid:reagent_id>/', get_inventory_reagent_data, name='inventory_reagent_data'),
    path('api/solution-base/<uuid:base_id>/', get_solution_base_data, name='solution_base_data'),
    path('add_standardization/<uuid:pk>/', StandardizationCreateView.as_view(), name='create_standardization'),
    path('update_standardization/<uuid:pk>/', StandardizationUpdateView.as_view(), name='update_standardization'),
    path('enable_base/<uuid:pk>/', SolutionBaseEnableView.as_view(), name='enable_solution_base'),
    path('enable_std_base/<uuid:pk>/', SolutionStdBaseEnableView.as_view(), name='enable_solution_std_base'),
    path('disable_base/<uuid:pk>/', SolutionBaseDisableView.as_view(), name='disable_solution_base'),
    path('disable_std_base/<uuid:pk>/', SolutionStdBaseDisableView.as_view(), name='disable_solution_std_base'),
    path('add_standardization_sln/<uuid:pk>/', StandardizationSolutionCreateView.as_view(), name='create_std_solution'),
    path('delete_standardization_sln/<uuid:pk>/', StandardizationSolutionDeleteView.as_view(),
         name='delete_standardization_solution'),
]

urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
