import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from alerts.models import Alert
from tests.factories import (
    AdminFactory,
    BPReadingFactory,
    ClinicianFactory,
    PatientFactory,
    UserFactory,
)

pytestmark = pytest.mark.django_db

class TestBPReadingListCreate:
    def test_patient_list_is_limited_to_own_recent_readings_and_filter(self):
        user = UserFactory(role='patient')
        own = PatientFactory(user=user)
        other = PatientFactory()
        own_reading = BPReadingFactory(patient=own)
        BPReadingFactory(patient=other)
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(
            reverse('bp-reading-list-create'), {'patient': own.id}
        )

        assert response.status_code == 200
        assert response.data['count'] == 1
        assert response.data['results'][0]['id'] == own_reading.id

    def test_admin_can_create_reading_for_any_patient(self):
        admin = AdminFactory()
        patient = PatientFactory()
        client = APIClient()
        client.force_authenticate(user=admin)

        response = client.post(reverse('bp-reading-list-create'), {
            'patient': patient.id,
            'systolic': 125,
            'diastolic': 75,
            'source': 'MANUAL',
        })

        assert response.status_code == 201

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
            'source': 'MANUAL',
            'recorded_at': '2026-06-23T10:00:00Z'   # Provide a valid datetime
        }
        response = client.post(url, data)
        assert response.status_code == 201
        assert Alert.objects.filter(patient=patient, severity='CRITICAL').exists()

    def test_clinician_cannot_add_reading_for_other_patient(self):
        clinician = ClinicianFactory()
        other_clinician = ClinicianFactory()
        patient = PatientFactory(clinician=other_clinician)
        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse('bp-reading-list-create')
        data = {
            'patient': patient.id,
            'systolic': 130,
            'diastolic': 85,
            'recorded_at': '2026-06-23T10:00:00Z'
        }
        response = client.post(url, data)
        assert response.status_code == 403

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
            'recorded_at': '2026-06-23T10:00:00Z'
        }
        response = client.post(url, data)
        assert response.status_code == 403

    def test_patient_add_endpoint_creates_own_reading(self):
        user = UserFactory(role='patient')
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(reverse('patient-add-reading'), {
            'systolic': 135,
            'diastolic': 85,
            'pulse_rate': 70,
        }, format='json')

        assert response.status_code == 201
        assert user.patient.filter(bp_readings__systolic=135).exists()

    def test_non_patient_cannot_use_patient_add_endpoint(self):
        clinician = ClinicianFactory()
        client = APIClient()
        client.force_authenticate(user=clinician)

        response = client.post(reverse('patient-add-reading'), {
            'systolic': 135,
            'diastolic': 85,
        }, format='json')

        assert response.status_code == 403
