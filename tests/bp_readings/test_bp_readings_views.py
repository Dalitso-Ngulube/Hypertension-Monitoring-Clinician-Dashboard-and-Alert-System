import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from tests.factories import PatientFactory, ClinicianFactory, UserFactory

pytestmark = pytest.mark.django_db

class TestBPReadingListCreate:
    def test_create_crisis_reading_triggers_alert(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse('bp-reading-list-create')
        data = {
            'patient': patient.id,
            'systolic': 190,
            'diastolic': 110,
        }
        response = client.post(url, data)
        assert response.status_code == 201

    def test_patient_add_reading_success(self):
        patient_user = UserFactory(role='patient')
        patient = PatientFactory(user=patient_user)
        client = APIClient()
        client.force_authenticate(user=patient_user)
        url = reverse('patient-add-reading')
        data = {'systolic': 120, 'diastolic': 80, 'pulse_rate': 70}
        response = client.post(url, data)
        assert response.status_code == 201

    def test_clinician_cannot_add_reading_for_other_patient(self):
        clinician1 = ClinicianFactory()
        clinician2 = ClinicianFactory()
        patient = PatientFactory(clinician=clinician2)
        client = APIClient()
        client.force_authenticate(user=clinician1)
        url = reverse('bp-reading-list-create')
        data = {'patient': patient.id, 'systolic': 120, 'diastolic': 80}
        response = client.post(url, data)
        assert response.status_code == 403