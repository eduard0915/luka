from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from core.product.views.product.views import *
from core.product.views.sample_point.views import *
from core.product.views.analytical_method.views import *

app_name = 'product'

urlpatterns = [
    # Productos
    path('add/', ProductCreateView.as_view(), name='create_product'),
    path('update/<uuid:pk>/', ProductUpdateView.as_view(), name='update_product'),
    path('detail/<uuid:pk>/', ProductDetailView.as_view(), name='detail_product'),
    path('list/', ProductListView.as_view(), name='list_product'),
    # Puntos de Muestreo
    path('add_sample_point/<uuid:pk>/', SamplePointCreateView.as_view(), name='create_sample_point'),
    path('update_sample_point/<uuid:pk>/', SamplePointUpdateView.as_view(), name='update_sample_point'),
    # Metodos Analíticos
    path('add_method/<uuid:pk>/', AnalyticalMethodProductCreateView.as_view(), name='create_method_product'),
    path('update_method/<uuid:pk>/', AnalyticalMethodProductUpdateView.as_view(), name='update_method_product'),
]

urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
