import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from tests.factories import PatientFactory, UserFactory, ClinicianFactory, AdminFactory

pytestmark = pytest.mark.django_db

class TestPatientListCreateView:
    def test_patient_sees_only_own_patients(self):
        patient_user = UserFactory(role='patient')
        own_patient = PatientFactory(user=patient_user, first_name="Mine")
        other_patient = PatientFactory()  # belongs to another patient user

        client = APIClient()
        client.force_authenticate(user=patient_user)
        url = reverse('patient-list-create')
        response = client.get(url)
        assert response.status_code == 200

        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == own_patient.id

    def test_clinician_sees_assigned_patients(self):
        clinician = ClinicianFactory()
        assigned = PatientFactory(clinician=clinician, first_name="Assigned")
        other = PatientFactory()  # unassigned

        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse('patient-list-create')
        response = client.get(url)
        assert response.status_code == 200
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == assigned.id


class TestPatientDetailView:
    def test_owner_can_retrieve(self):
        patient_user = UserFactory(role='patient')
        patient = PatientFactory(user=patient_user)

        client = APIClient()
        client.force_authenticate(user=patient_user)
        url = reverse('patient-detail', args=[patient.id])
        response = client.get(url)
        assert response.status_code == 200
        assert response.data['id'] == patient.id
    def test_patient_sees_only_own_data(self):
        patient_user = UserFactory(role='patient')
        patient = PatientFactory(user=patient_user)
        client = APIClient()
        client.force_authenticate(user=patient_user)
        url = reverse('patient-detail', args=[patient.id])
        response = client.get(url)
        assert response.status_code == 200
        # Assert that password or other sensitive fields are absent
        assert 'password' not in response.data
    def test_other_patient_cannot_access(self):
        owner = UserFactory(role='patient')
        other = UserFactory(role='patient')
        patient = PatientFactory(user=owner)

        client = APIClient()
        client.force_authenticate(user=other)
        url = reverse('patient-detail', args=[patient.id])
        response = client.get(url)
        assert response.status_code == 403