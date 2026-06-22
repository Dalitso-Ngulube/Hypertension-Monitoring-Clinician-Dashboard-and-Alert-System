import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from tests.factories import PatientFactory, ClinicianFactory, AdminFactory, UserFactory
from alerts.models import Alert

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
            'pulse_rate': 85,
            'source': 'MANUAL'
        }
        response = client.post(url, data)
        assert response.status_code == 201
        # Alert should be created
        assert Alert.objects.filter(patient=patient, severity='CRITICAL').exists()
        alert = Alert.objects.get(patient=patient)
        assert alert.message.startswith("CRISIS reading:")

    def test_normal_reading_no_alert(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse('bp-reading-list-create')
        data = {
            'patient': patient.id,
            'systolic': 110,
            'diastolic': 70,
        }
        response = client.post(url, data)
        assert response.status_code == 201
        assert Alert.objects.filter(patient=patient).count() == 0

    def test_patient_cannot_create_reading_for_other_patient(self):
        patient_user = UserFactory(role='patient')
        own_patient = PatientFactory(user=patient_user)
        other_patient = PatientFactory()
        client = APIClient()
        client.force_authenticate(user=patient_user)
        url = reverse('bp-reading-list-create')
        data = {
            'patient': other_patient.id,
            'systolic': 130,
            'diastolic': 85,
        }
        response = client.post(url, data)
        assert response.status_code == 403