from django.urls import path
from core.condition.views import (
    ConditionListView, ConditionCreateView, ConditionUpdateView,
    ConditionRegisterListView, ConditionRegisterCreateView, ConditionRegisterUpdateView,
    ConditionRegisterActionsUpdateView, ConditionVariableAPI, ConditionRegisterDetailView
)

app_name = 'condition'

urlpatterns = [
    path('list/', ConditionListView.as_view(), name='list_condition'),
    path('add/', ConditionCreateView.as_view(), name='create_condition'),
    path('update/<uuid:pk>/', ConditionUpdateView.as_view(), name='update_condition'),
    path('variable/api/', ConditionVariableAPI.as_view(), name='condition_variable_api'),

    path('register/list/', ConditionRegisterListView.as_view(), name='list_condition_register'),
    path('register/add/', ConditionRegisterCreateView.as_view(), name='create_condition_register'),
    path('register/update/<uuid:pk>/', ConditionRegisterUpdateView.as_view(), name='update_condition_register'),
    path('register/actions/<uuid:pk>/', ConditionRegisterActionsUpdateView.as_view(), name='update_condition_register_actions'),
    path('register/detail/<uuid:pk>/', ConditionRegisterDetailView.as_view(), name='detail_condition_register'),
]
