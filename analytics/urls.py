from django.urls import path
from .views import (
    PatientTrendView,
    AnalyticsSummaryView,
    RiskDistributionView,
    RiskScoreView,  BPTrendView
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
]
