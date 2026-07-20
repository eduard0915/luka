from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from core.product.views.product.views import *
from core.product.views.sample_point.views import *
from core.product.views.analytical_method.views import *
from core.product.views.specification.views import *
from core.product.views.analytical_method_relation.views import *

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
    path('detail_sample_point/<uuid:pk>/', SamplePointDetailView.as_view(), name='detail_sample_point'),
    path('delete_sample_point/<uuid:pk>/', SamplePointDeleteView.as_view(), name='delete_sample_point'),
    # Métodos Analíticos
    path('add_method/<uuid:pk>/', AnalyticalMethodProductCreateView.as_view(), name='create_method_product'),
    path('update_method/<uuid:pk>/', AnalyticalMethodProductUpdateView.as_view(), name='update_method_product'),
    # Especificaciones
    path('add_specification/<uuid:pk>/', SpecificationProductCreateView.as_view(), name='create_specification_product'),
    path('update_specification/<uuid:pk>/', SpecificationProductUpdateView.as_view(), name='update_specification_product'),
    path('delete_specification/<uuid:pk>/', SpecificationProductDeleteView.as_view(), name='delete_specification_product'),
    path('add_specification_calcule_relation/<uuid:pk>/', SpecificationProductCalculeCreateView.as_view(), name='create_specification_product_calcule'),
    path('update_specification_calcule_relation/<uuid:pk>/', SpecificationProductCalculeUpdateView.as_view(), name='update_specification_product_calcule'),
    # Cálculos Dependientes de Productos
    path('add_calc_relation_description/<uuid:pk>/', ProductCalculateRelationDescriptionCreateView.as_view(), name='add_calc_relation_description'),
    path('edit_calc_relation_description/<uuid:pk>/', ProductCalculateRelationDescriptionUpdateView.as_view(), name='edit_calc_relation_description'),
    path('add_calc_relation/<uuid:pk>/', ProductCalculateRelationCreateView.as_view(), name='add_calc_relation'),
    path('edit_calc_relation/<uuid:pk>/', ProductCalculateRelationUpdateView.as_view(), name='edit_calc_relation'),
    path('add_volume_relation_std/<uuid:pk>/', ProductVolumenStdRelationCreateView.as_view(), name='add_volume_relation_std'),
    path('edit_volume_relation_std/<uuid:pk>/', ProductVolumenStdRelationUpdateView.as_view(), name='edit_volume_relation_std'),
    path('add_factor_relation/<uuid:pk>/', ProductFactorRelationCreateView.as_view(), name='add_factor_relation'),
    path('edit_factor_relation/<uuid:pk>/', ProductFactorRelationUpdateView.as_view(), name='edit_factor_relation'),
    path('add_sample_gram_relation/<uuid:pk>/', ProductSampleGramRelationCreateView.as_view(), name='add_sample_gram_relation'),
    path('edit_sample_gram_relation/<uuid:pk>/', ProductSampleGramRelationUpdateView.as_view(), name='edit_sample_gram_relation'),
    path('delete_calc_relation/<uuid:pk>/', ProductCalculateRelationDeleteView.as_view(), name='delete_calc_relation'),
]

urlpatterns += static(settings.MEDIA_URL,
                      document_root=settings.MEDIA_ROOT)
