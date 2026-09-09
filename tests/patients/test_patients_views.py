import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from tests.factories import ClinicianFactory, PatientFactory, UserFactory

pytestmark = pytest.mark.django_db

class TestPatientListCreateView:
    def test_patient_sees_only_own_patients(self):
        patient_user = UserFactory(role='patient')      # signal creates Patient automatically
        other_user = UserFactory(role='patient')        # separate user for comparison

        client = APIClient()
        client.force_authenticate(user=patient_user)
        url = reverse('patient-list-create')
        response = client.get(url)
        assert response.status_code == 200
        # Should only see the one patient created by the signal for this user
        assert response.data['count'] == 1

    def test_clinician_sees_assigned_patients(self):
        clinician = ClinicianFactory()
        assigned = PatientFactory(clinician=clinician)   # explicit creation, no signal for clinician
        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse('patient-list-create')
        response = client.get(url)
        assert response.status_code == 200
        assert response.data['count'] == 1


class TestPatientDetailView:
    def test_patient_cannot_access_other_patients(self):
        patient_user = UserFactory(role='patient')
        other_user = UserFactory(role='patient')
        other_patient = PatientFactory(user=other_user)  # explicit creation (or could rely on signal)
        client = APIClient()
        client.force_authenticate(user=patient_user)
        url = reverse('patient-detail', args=[other_patient.id])
        response = client.get(url)
        assert response.status_code == 403

    def test_patient_medical_history_get(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse('patient-medical-history', kwargs={'patient_id': patient.id})
        response = client.get(url)
        assert response.status_code == 200
        assert 'smoking_status' in response.data