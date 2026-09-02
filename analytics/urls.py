from django.urls import path

from .views import (
    AnalyticsSummaryView,
    BPTrendView,
    ClinicalDecisionSupportView,
    ExportAllPatientsSummaryCSV,
    ExportPatientDataCSV,
    PatientTimeOfDayPatternsView,
    PatientTrendView,
    RiskDistributionView,
    RiskScoreView,
)

urlpatterns = [

    path(
        'patient/<int:patient_id>/trend/',
        PatientTrendView.as_view(),
        name='patient-trend'
    ),
    path('trends/<int:patient_id>/', BPTrendView.as_view(), name='bp-trend'),
    path(
        'summary/',
        AnalyticsSummaryView.as_view(),
        name='analytics-summary'
    ),
    path(
        'risk-distribution/',
        RiskDistributionView.as_view(),
        name='risk-distribution'
    ),
    path('risk-score/<int:patient_id>/', RiskScoreView.as_view(), name='risk-score'),
    path('patient/<int:patient_id>/time-patterns/', PatientTimeOfDayPatternsView.as_view(), name='time-patterns'),
    path('export/patient/<int:patient_id>/', ExportPatientDataCSV.as_view(), name='export-patient-csv'),
    path('export/summary/', ExportAllPatientsSummaryCSV.as_view(), name='export-summary-csv'),
    path('cds/<int:patient_id>/', ClinicalDecisionSupportView.as_view(), name='clinical-decision-support'),
]
