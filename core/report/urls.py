from django.urls import path
from core.report.views import SamplingAnalysisListView, SamplingAnalysisByPointListView, SamplingAnalysisChartView, \
    SamplingAnalysisByPointExcelView, SamplingAnalysisProcessingListView, SamplingAnalysisProcessingExcelView

app_name = 'report'

urlpatterns = [
    path('sampling/analysis/list/', SamplingAnalysisListView.as_view(), name='sampling_analysis_list'),
    path('sampling/analysis/list/point/', SamplingAnalysisByPointListView.as_view(), name='sampling_analysis_list_point'),
    path('sampling/analysis/chart/', SamplingAnalysisChartView.as_view(), name='sampling_analysis_chart'),
    path('sampling/analysis/list/point/excel/', SamplingAnalysisByPointExcelView.as_view(), name='sampling_analysis_list_point_excel'),
    path('sampling/analysis/processing/list/', SamplingAnalysisProcessingListView.as_view(), name='sampling_analysis_processing_list'),
    path('sampling/analysis/processing/excel/', SamplingAnalysisProcessingExcelView.as_view(), name='sampling_analysis_processing_excel'),
]
