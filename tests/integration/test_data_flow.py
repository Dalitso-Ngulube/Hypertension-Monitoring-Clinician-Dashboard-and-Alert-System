import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from alerts.models import Alert
from tests.factories import ClinicianFactory, PatientFactory

pytestmark = pytest.mark.django_db

def test_clinician_creates_patient_adds_reading_and_resolves_alert():
    clinician = ClinicianFactory()
    client = APIClient()
    client.force_authenticate(user=clinician)

    patient = PatientFactory(clinician=clinician)

    reading_data = {
        'patient': patient.id,
        'systolic': 190,
        'diastolic': 110,
        'recorded_at': '2026-06-23T10:00:00Z'
    }
    url = reverse('bp-reading-list-create')
    response = client.post(url, reading_data)
    assert response.status_code == 201

    alert = Alert.objects.filter(patient=patient, alert_type='CRISIS').first()
    assert alert is not None
    assert alert.severity == 'CRITICAL'
    assert alert.is_resolved is False

    url = reverse('alert-update', args=[alert.id])
    response = client.patch(url, {'is_resolved': True})
    assert response.status_code == 200
    alert.refresh_from_db()
    assert alert.is_resolved is True
