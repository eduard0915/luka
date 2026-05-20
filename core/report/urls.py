from django.urls import path
from core.report.views import SamplingAnalysisListView, SamplingAnalysisByPointListView

app_name = 'report'

urlpatterns = [
    path('sampling/analysis/list/', SamplingAnalysisListView.as_view(), name='sampling_analysis_list'),
    path('sampling/analysis/list/point/', SamplingAnalysisByPointListView.as_view(), name='sampling_analysis_list_point'),
]
