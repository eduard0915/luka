from django.conf.urls.static import static
from django.urls import path

from core.analytical_method.views.calculate.views import *
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

    # Detalles de Métodos Analíticos
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
    path('detail/calculate/add_volumen_std_den/<uuid:pk>/', AnalyticalMethodVolumenStdCreateView.as_view(), name='add_volume_std'),
    path('detail/calculate/add_factor_den/<uuid:pk>/', AnalyticalMethodFactorCreateView.as_view(), name='add_factor'),
    path('detail/calculate/add_sample_gram/<uuid:pk>/', AnalyticalMethodSampleGramCreateView.as_view(), name='add_sample_gram'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
