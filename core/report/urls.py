from django.urls import path
from core.report.views import SamplingAnalysisListView, SamplingAnalysisByPointListView, SamplingAnalysisChartView, SamplingAnalysisByPointExcelView

app_name = 'report'

urlpatterns = [
    path('sampling/analysis/list/', SamplingAnalysisListView.as_view(), name='sampling_analysis_list'),
    path('sampling/analysis/list/point/', SamplingAnalysisByPointListView.as_view(), name='sampling_analysis_list_point'),
    path('sampling/analysis/chart/', SamplingAnalysisChartView.as_view(), name='sampling_analysis_chart'),
    path('sampling/analysis/list/point/excel/', SamplingAnalysisByPointExcelView.as_view(), name='sampling_analysis_list_point_excel'),
]
