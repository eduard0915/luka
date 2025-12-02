from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from core.product.views.product.views import ProductCreateView, ProductUpdateView, ProductListView, ProductDetailView
from core.product.views.sample_point.views import SamplePointCreateView, SamplePointUpdateView
from core.product.views.stage.views import StageCreateView, StageUpdateView

app_name = 'product'

urlpatterns = [
    # Productos
    path('add/', ProductCreateView.as_view(), name='create_product'),
    path('update/<uuid:pk>/', ProductUpdateView.as_view(), name='update_product'),
    path('detail/<uuid:pk>/', ProductDetailView.as_view(), name='detail_product'),
    path('list/', ProductListView.as_view(), name='list_product'),
    # Etapas
    path('add_stage/<uuid:pk>/', StageCreateView.as_view(), name='create_stage'),
    path('update_stage/<uuid:pk>/', StageUpdateView.as_view(), name='update_stage'),
    # Puntos de Muestreo
    path('add_sample_point/<uuid:pk>/', SamplePointCreateView.as_view(), name='create_sample_point'),
    path('update_sample_point/<uuid:pk>/', SamplePointUpdateView.as_view(), name='update_sample_point')
]

urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
