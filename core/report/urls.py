from django.urls import path
from core.report.views import SamplingAnalysisListView

app_name = 'report'

urlpatterns = [
    path('sampling/analysis/list/', SamplingAnalysisListView.as_view(), name='sampling_analysis_list'),
]
