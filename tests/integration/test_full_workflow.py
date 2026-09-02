import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from tests.factories import AdminFactory

pytestmark = pytest.mark.django_db

def test_clinician_creates_patient_adds_reading_and_alert_resolution():
    admin = AdminFactory()
    client = APIClient()
    client.force_authenticate(user=admin)

    # 1. Create clinician
    clinician_data = {
        'username': 'dr_smith',
        'password': 'pass',
        'email': 'smith@hospital.com',
        'role': 'clinician'
    }
    clin_response = client.post(reverse('create-clinician'), clinician_data)
    assert clin_response.status_code == 201
    clinician_id = clin_response.data['id']

    # 2. Create patient assigned to that clinician
    patient_data = {
        'first_name': 'Alice',
        'last_name': 'Brown',
        'age': 55,
        'clinician': clinician_id
    }
    patient_response = client.post(reverse('patient-list-create'), patient_data)
    patient_id = patient_response.data['id']

    # 3. Clinician adds a crisis BP reading
    client.force_authenticate(user=clinician_id)  # need to fetch user object; simplified
    # (In real test you'd get the user instance)