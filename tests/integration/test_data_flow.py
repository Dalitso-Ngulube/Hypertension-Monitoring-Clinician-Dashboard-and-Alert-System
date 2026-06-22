import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from tests.factories import UserFactory, PatientFactory, ClinicianFactory
from alerts.models import Alert

pytestmark = pytest.mark.django_db

def test_clinician_creates_patient_adds_reading_and_resolves_alert():
    clinician = UserFactory(role='clinician')
    client = APIClient()
    client.force_authenticate(user=clinician)

    # 1. Create a patient (via factory to ensure clinician is assigned)
    patient = PatientFactory(clinician=clinician)
    patient_id = patient.id

    # 2. Add a CRISIS BP reading
    reading_data = {'patient': patient_id, 'systolic': 190, 'diastolic': 110}
    url = reverse('bp-reading-list-create')
    response = client.post(url, reading_data)
    assert response.status_code == 201

    # 3. Verify alert was auto-created
    alert = Alert.objects.get(patient_id=patient_id)
    assert alert.severity == 'CRITICAL'
    assert alert.is_resolved is False
    assert "CRISIS" in alert.message

    # 4. Clinician resolves the alert
    url = reverse('alert-update', args=[alert.id])
    response = client.patch(url, {'is_resolved': True})
    assert response.status_code == 200
    alert.refresh_from_db()
    assert alert.is_resolved is True