from django.urls import path
from core.observation.views import ObservationCreateView, ObservationUpdateView

app_name = 'observation'

urlpatterns = [
    path('add/<uuid:pk>/', ObservationCreateView.as_view(), name='observation_create'),
    path('update/<uuid:pk>/', ObservationUpdateView.as_view(), name='observation_update'),
]
