from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from core.company.views.company.views import *
from core.company.views.process.views import *
from core.company.views.site.views import SiteCreateView, SiteUpdateView, SiteDetailView

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
    # Procesos
    path('add_process/<uuid:pk>/', ProcessCreateView.as_view(), name='create_process'),
    path('update_process/<uuid:pk>/', ProcessUpdateView.as_view(), name='update_process')
]

urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
