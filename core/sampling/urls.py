"""Definición de rutas URL para la aplicación de muestreo."""

from django.conf.urls.static import static
from django.urls import path

from core.sampling.views.group_sampling.views import *
from core.sampling.views.process_sampling.views import *
from core.sampling.views.analysis_sampling.views import *
from luka import settings

app_name = 'sampling'

urlpatterns = [
    # Grupos de Muestreo
    path('group/add/', SamplingGroupCreateView.as_view(), name='create_sampling_group'),
    path('group/list/', SamplingGroupListView.as_view(), name='list_sampling_group'),
    path('group/update/<uuid:pk>/', SamplingGroupUpdateView.as_view(), name='update_sampling_group'),
    path('group/detail/<uuid:pk>/', SamplingGroupDetailView.as_view(), name='detail_sampling_group'),
    path('api/sampling-point/<uuid:pk>/', get_sampling_point, name='get_sampling_point'),
    # Procesos de Muestreo
    path('process/add/', SamplingProcessCreateView.as_view(), name='create_sampling_process'),
    path('process/list/', SamplingProcessListView.as_view(), name='list_sampling_process'),
    path('process/list/scheduled/', SamplingProcessScheduledListView.as_view(), name='list_sampling_process_scheduled'),
    path('process/list/confirmed/', SamplingProcessConfirmedListView.as_view(), name='list_sampling_process_confirmed'),
    path('process/list/in-process/', SamplingProcessInProcessListView.as_view(), name='list_sampling_process_in_process'),
    path('process/list/out-specification/', SamplingProcessOutSpecificationListView.as_view(), name='list_sampling_process_out_specification'),
    path('process/update/<uuid:pk>/', SamplingProcessUpdateView.as_view(), name='update_sampling_process'),
    path('process/detail/<uuid:pk>/', SamplingProcessDetailView.as_view(), name='detail_sampling_process'),
    path('process/update-image/<uuid:pk>/', SamplingProcessImageUpdateView.as_view(), name='update_image_sample'),
    path('process/confirmed/<uuid:pk>/', SamplingProcessConfirmedUpdateView.as_view(), name='confirmed_sampling_process'),
    path('process/approved/<uuid:pk>/', SamplingProcessApprovedUpdateView.as_view(), name='approved_sampling_process'),
    path('analysis/inprocess/<uuid:pk>/<uuid:analysis_id>/', SamplingProcessInProcessUpdateView.as_view(), name='sampling_in_process_with_analysis'),
    # Procesamiento de la muestra
    path('analysis/detail/<uuid:pk>/', SamplingAnalysisDetailView.as_view(), name='detail_sampling_analysis'),
    path('analysis/processing_volumetry/add/<uuid:pk>/', SamplingAnalysisProcessingCreateView.as_view(), name='sampling_analysis_volumetry'),
    path('analysis/processing_gravimetry/add/<uuid:pk>/', SamplingAnalysisProcessingGravimetryCreateView.as_view(), name='sampling_analysis_gravimetry'),
    path('analysis/processing_direct/add/<uuid:pk>/', SamplingAnalysisProcessingDirectCreateView.as_view(), name='sampling_analysis_direct'),
    path('analysis/processing/relation/add/<uuid:pk>/', SamplingAnalysisProcessingRelationCreateView.as_view(), name='create_sampling_analysis_processing_relation'),
    path('analysis/processing/relation/delete/<uuid:pk>/', SamplingAnalysisProcessingRelationDeleteView.as_view(), name='delete_sampling_analysis_processing_relation'),
    # Análisis volumétrico por retroceso
    path('analysis/millimole/add/<uuid:pk>/', MillimoleReactedCreateView.as_view(), name='create_millimole_reacted'),
    path('analysis/millimole/delete/<uuid:pk>/', MillimoleReactedDeleteView.as_view(), name='delete_millimole_reacted'),
    # Análisis de la Muestra (CRUD)
    path('analysis/list/', SamplingAnalysisListView.as_view(), name='list_sampling_analysis'), # Sin usar
    path('analysis/processing/list/', SamplingAnalysisProcessingListView.as_view(), name='list_sampling_analysis_processing'),
    path('analysis/add/<uuid:pk>/', SamplingAnalysisCreateView.as_view(), name='create_sampling_analysis'),
    path('analysis/delete/<uuid:pk>/', SamplingAnalysisDeleteView.as_view(), name='delete_sampling_analysis'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
