from django.conf.urls.static import static
from django.urls import path

from core.analytical_method.views.calculate.views import *
from core.analytical_method.views.calculate_relation.views import *
from core.analytical_method.views.method.views import *
from core.analytical_method.views.detail_method.views import *
from luka import settings

app_name = 'analytical_method'

urlpatterns = [
    # Métodos Analíticos
    path('add/', AnalyticalMethodCreateView.as_view(), name='create_method'),
    path('list/', AnalyticalMethodListView.as_view(), name='list_method'),
    path('update/<uuid:pk>/', AnalyticalMethodUpdateView.as_view(), name='update_method'),
    path('detail/<uuid:pk>/', AnalyticalMethodDetailView.as_view(), name='detail_method'),

    # Soluciones
    path('detail/solution/add/<uuid:pk>/', AnalyticalMethodSolutionCreateView.as_view(), name='add_solution'),
    path('detail/solution/update/<uuid:pk>/', AnalyticalMethodSolutionUpdateView.as_view(), name='update_solution'),

    # Soluciones Estándar
    path('detail/solution_std/add/<uuid:pk>/', AnalyticalMethodSolutionStdCreateView.as_view(), name='add_solution_std'),
    path('detail/solution_std/update/<uuid:pk>/', AnalyticalMethodSolutionStdUpdateView.as_view(), name='update_solution_std'),

    # Reactivos
    path('detail/reagent/add/<uuid:pk>/', AnalyticalMethodReagentCreateView.as_view(), name='add_reagent'),
    path('detail/reagent/update/<uuid:pk>/', AnalyticalMethodReagentUpdateView.as_view(), name='update_reagent'),

    # Equipos
    path('detail/equipment/add/<uuid:pk>/', AnalyticalMethodEquipmentCreateView.as_view(), name='add_equipment'),
    path('detail/equipment/update/<uuid:pk>/', AnalyticalMethodEquipmentUpdateView.as_view(), name='update_equipment'),

    # Materiales
    path('detail/material/add/<uuid:pk>/', AnalyticalMethodMaterialCreateView.as_view(), name='add_material'),
    path('detail/material/update/<uuid:pk>/', AnalyticalMethodMaterialUpdateView.as_view(), name='update_material'),

    # Procedimientos
    path('detail/procedure/add/<uuid:pk>/', AnalyticalMethodProcedureCreateView.as_view(), name='add_procedure'),
    path('detail/procedure/update/<uuid:pk>/', AnalyticalMethodProcedureUpdateView.as_view(), name='update_procedure'),

    # Cálculos
    path('detail/calculate/add_description/<uuid:pk>/', AnalyticalMethodCalculeDescriptionCreateView.as_view(), name='add_calc_description'),
    path('detail/calculate/edit_description/<uuid:pk>/', AnalyticalMethodCalculeDescriptionUpdateView.as_view(), name='edit_calc_description'),
    path('detail/calculate/add_volumen_std_den/<uuid:pk>/', AnalyticalMethodVolumenStdCreateView.as_view(), name='add_volume_std'),
    path('detail/calculate/edit_volumen_std_den/<uuid:pk>/', AnalyticalMethodVolumenStdUpdateView.as_view(), name='edit_volume_std'),
    path('detail/calculate/add_factor_den/<uuid:pk>/', AnalyticalMethodFactorCreateView.as_view(), name='add_factor'),
    path('detail/calculate/edit_factor_den/<uuid:pk>/', AnalyticalMethodFactorUpdateView.as_view(), name='edit_factor'),
    path('detail/calculate/add_sample_gram/<uuid:pk>/', AnalyticalMethodSampleGramCreateView.as_view(), name='add_sample_gram'),
    path('detail/calculate/edit_sample_gram/<uuid:pk>/', AnalyticalMethodSampleGramUpdateView.as_view(), name='edit_sample_gram'),
    path('detail/calculate/delete/<uuid:pk>/', AnalyticalMethodCalculateDeleteView.as_view(), name='delete_analytical_method_calcule'),

    # Cálculos Relacionados
    path('detail/calculate_relation/add_description/<uuid:pk>/', AnalyticalMethodCalculeRelationDescriptionCreateView.as_view(), name='add_calc_relation_description'),
    path('detail/calculate_relation/edit_description/<uuid:pk>/', AnalyticalMethodCalculeRelationDescriptionUpdateView.as_view(), name='edit_calc_relation_description'),
    path('detail/calculate_relation/add_relation/<uuid:pk>/', AnalyticalMethodCalculateRelationCreateView.as_view(), name='add_calc_relation'),
    path('detail/calculate_relation/edit_relation/<uuid:pk>/', AnalyticalMethodCalculateRelationUpdateView.as_view(), name='edit_calc_relation'),
    path('detail/calculate_relation/add_volumen_std_den/<uuid:pk>/', AnalyticalMethodVolumenStdRelationCreateView.as_view(), name='add_volume_relation_std'),
    path('detail/calculate_relation/edit_volumen_std_den/<uuid:pk>/', AnalyticalMethodVolumenStdRelationUpdateView.as_view(), name='edit_volume_relation_std'),
    path('detail/calculate_relation/add_factor_den/<uuid:pk>/', AnalyticalMethodFactorRelationCreateView.as_view(), name='add_factor_relation'),
    path('detail/calculate_relation/edit_factor_den/<uuid:pk>/', AnalyticalMethodFactorRelationUpdateView.as_view(), name='edit_factor_relation'),
    path('detail/calculate_relation/add_sample_gram/<uuid:pk>/', AnalyticalMethodSampleGramRelationCreateView.as_view(), name='add_sample_gram_relation'),
    path('detail/calculate_relation/edit_sample_gram/<uuid:pk>/', AnalyticalMethodSampleGramRelationUpdateView.as_view(), name='edit_sample_gram_relation'),
    path('detail/calculate_relation/delete/<uuid:pk>/', AnalyticalMethodCalculateRelationDeleteView.as_view(), name='delete_analytical_method_calcule_relation'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
