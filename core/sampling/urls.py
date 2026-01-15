from django.conf.urls.static import static
from django.urls import path

from core.sampling.views.group_sampling.views import *
from core.sampling.views.process_sampling.views import *
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
    path('process/update/<uuid:pk>/', SamplingProcessUpdateView.as_view(), name='update_sampling_process'),
    path('process/detail/<uuid:pk>/', SamplingProcessDetailView.as_view(), name='detail_sampling_process'),
    path('process/update-image/<uuid:pk>/', SamplingProcessImageUpdateView.as_view(), name='update_image_sample'),
    path('process/confirmed/<uuid:pk>/', SamplingProcessConfirmedUpdateView.as_view(), name='confirmed_sampling_process'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
