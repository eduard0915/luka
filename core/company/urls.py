from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from core.company.views.company.views import *
from core.company.views.process.views import *
from core.company.views.sample_point.views import *
from core.company.views.site.views import *
from core.company.views.stage.views import *

app_name = 'company'

urlpatterns = [
    # Company
    path('add/', CompanyCreateView.as_view(), name='company_create'),
    path('update/<uuid:pk>/', CompanyUpdateView.as_view(), name='company_update'),
    path('detail/<uuid:pk>/', CompanyDetailView.as_view(), name='company_detail'),
    # Plantas
    path('add_site/', SiteCreateView.as_view(), name='create_site'),
    path('update_site/<uuid:pk>/', SiteUpdateView.as_view(), name='update_site'),
    path('detail_site/<uuid:pk>/', SiteDetailView.as_view(), name='detail_site'),
    path('list_site/', SiteListView.as_view(), name='list_site'),
    # Procesos
    path('add_process/<uuid:pk>/', ProcessCreateView.as_view(), name='create_process'),
    path('update_process/<uuid:pk>/', ProcessUpdateView.as_view(), name='update_process'),
    # Etapas
    path('add_stage/<uuid:pk>/', StageCreateView.as_view(), name='create_stage'),
    path('update_stage/<uuid:pk>/', StageUpdateView.as_view(), name='update_stage'),
    # Puntos de Muestreo
    path('add_sample_point/<uuid:pk>/', SamplePointCreateView.as_view(), name='create_sample_point'),
    path('update_sample_point/<uuid:pk>/', SamplePointUpdateView.as_view(), name='update_sample_point')
]

urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
