from django.urls import path
from .views import (
    PatientListCreateView,
    PatientDetailView,
    PatientMedicalHistoryView,
    MedicalConditionListView,
    AllergyListView,
    MedicationListView,
)



urlpatterns = [
    path(
        '', PatientListCreateView.as_view(),
        name='patient-list-create'
    ),
    path('<int:pk>/', PatientDetailView.as_view(), name='patient-detail'),
    path('<int:patient_id>/medical-history/', PatientMedicalHistoryView.as_view(), name='patient-medical-history'),
    path('reference/conditions/', MedicalConditionListView.as_view(), name='medical-conditions'),
    path('reference/allergies/', AllergyListView.as_view(), name='allergies'),
    path('reference/medications/', MedicationListView.as_view(), name='medications'),
]
