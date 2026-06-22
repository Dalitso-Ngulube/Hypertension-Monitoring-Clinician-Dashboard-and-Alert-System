import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from tests.factories import AlertFactory, ClinicianFactory, PatientFactory, UserFactory
from alerts.models import Alert

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
        # ✅ FIX: use response.data['results'] because pagination is enabled
        assert len(response.data['results']) == 1

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