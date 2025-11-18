from django.conf.urls.static import static
from django.urls import path

from core.laboratory.views.lab.views import *
from luka import settings

app_name = 'laboratory'

urlpatterns = [
    path('add/', LaboratoryCreateView.as_view(), name='create_laboratory'),
    path('list/', LaboratoryListView.as_view(), name='list_laboratory'),
    path('update/<uuid:pk>/', LaboratoryUpdateView.as_view(), name='update_laboratory'),
    path('detail/<uuid:pk>/', LaboratoryDetailView.as_view(), name='detail_laboratory'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
