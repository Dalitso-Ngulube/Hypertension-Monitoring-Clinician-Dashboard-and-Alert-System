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

    def test_patient_can_list_only_their_appointments(self):
        patient_user = PatientFactory().user
        patient = PatientFactory(user=patient_user)
        AppointmentFactory(patient=patient)
        other_appointment = AppointmentFactory()
        client = APIClient()
        client.force_authenticate(user=patient_user)

        response = client.get(reverse('appointment-list'))

        assert response.status_code == 200
        returned_ids = {item['id'] for item in response.data['results']}
        assert other_appointment.id not in returned_ids

    def test_patient_cannot_create_appointment(self):
        patient = PatientFactory()
        client = APIClient()
        client.force_authenticate(user=patient.user)

        response = client.post(reverse('appointment-list'), {
            'patient': patient.id,
            'date': '2026-09-01',
            'time': '10:00:00',
            'reason': 'Checkup',
        })

        assert response.status_code == 403