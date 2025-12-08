from django.conf.urls.static import static
from django.urls import path

from core.analytical_method.views.method.views import *
from luka import settings

app_name = 'analytical_method'

urlpatterns = [
    path('add/', AnalyticalMethodCreateView.as_view(), name='create_method'),
    path('list/', AnalyticalMethodListView.as_view(), name='list_method'),
    path('update/<uuid:pk>/', AnalyticalMethodUpdateView.as_view(), name='update_method'),
    path('detail/<uuid:pk>/', AnalyticalMethodDetailView.as_view(), name='detail_method'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
