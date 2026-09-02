import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from tests.factories import AppointmentFactory, ClinicianFactory, PatientFactory

pytestmark = pytest.mark.django_db

class TestAppointmentViewSet:
    def test_list_appointments_clinician(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        AppointmentFactory(patient=patient, clinician=clinician)
        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse('appointment-list')
        response = client.get(url)
        assert response.status_code == 200

    def test_create_appointment_clinician(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse('appointment-list')
        data = {
            'patient': patient.id,
            'date': '2026-09-01',
            'time': '10:00:00',
            'reason': 'Checkup'
        }
        response = client.post(url, data)
        assert response.status_code == 201