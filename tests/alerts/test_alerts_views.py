import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import AuditLog
from tests.factories import AlertFactory, ClinicianFactory, PatientFactory

pytestmark = pytest.mark.django_db

class TestAlertListCreateView:
    def test_clinician_sees_only_alerts_of_their_patients(self):
        clinician = ClinicianFactory()
        other_clinician = ClinicianFactory()
        my_patient = PatientFactory(clinician=clinician)
        other_patient = PatientFactory(clinician=other_clinician)
        AlertFactory(patient=my_patient)
        AlertFactory(patient=other_patient)

        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse('alert-list')
        response = client.get(url)
        assert response.status_code == 200
        assert response.data['count'] == 1

class TestUnresolvedAlertsView:
    def test_only_unresolved_alerts_returned(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        AlertFactory(patient=patient, is_resolved=False)
        AlertFactory(patient=patient, is_resolved=True)

        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse('unresolved-alerts')
        response = client.get(url)
        assert response.status_code == 200
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['is_resolved'] is False

    def test_alert_create(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse('alert-list')
        data = {
            'patient': patient.id,
            'severity': 'HIGH',
            'message': 'Test alert'
        }
        response = client.post(url, data)
        assert response.status_code == 201
        assert response.data['is_resolved'] is False

    def test_alert_resolve(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        alert = AlertFactory(patient=patient, is_resolved=False)
        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse('alert-update', args=[alert.id])
        response = client.patch(url, {'is_resolved': True})
        assert response.status_code == 200
        assert response.data['is_resolved'] is True
        audit = AuditLog.objects.get(
            action='UPDATE',
            resource_type='alerts.Alert',
            resource_id=alert.id,
        )
        assert audit.user == clinician
        assert audit.details['event'] == 'alert_resolved'