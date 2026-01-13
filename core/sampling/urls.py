from django.conf.urls.static import static
from django.urls import path

from core.sampling.views.group_sampling.views import *
from luka import settings

app_name = 'sampling'

urlpatterns = [
    # Grupos de Muestreo
    path('group/add/', SamplingGroupCreateView.as_view(), name='create_sampling_group'),
    path('group/list/', SamplingGroupListView.as_view(), name='list_sampling_group'),
    path('group/update/<uuid:pk>/', SamplingGroupUpdateView.as_view(), name='update_sampling_group'),
    path('group/detail/<uuid:pk>/', SamplingGroupDetailView.as_view(), name='detail_sampling_group'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
