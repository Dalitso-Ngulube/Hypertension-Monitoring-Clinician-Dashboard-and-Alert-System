from django.urls import path
from .views import (
    PatientTrendView,
    AnalyticsSummaryView,
    RiskDistributionView,
)

urlpatterns = [

    path(
        'patient/<int:patient_id>/trend/',
        PatientTrendView.as_view(),
        name='patient-trend'
    ),

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
]