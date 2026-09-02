import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from tests.factories import ClinicianFactory, PatientFactory, UserFactory

pytestmark = pytest.mark.django_db

def test_patient_cannot_access_admin_only_endpoint():
    patient = UserFactory(role='patient')
    client = APIClient()
    client.force_authenticate(user=patient)
    # Use an admin-only endpoint that definitely exists
    url = reverse('create-clinician')
    # GET may not be allowed, but the permission check still runs
    response = client.get(url)
    assert response.status_code == 403

def test_patient_cannot_modify_other_patients():
    patient1 = UserFactory(role='patient')
    patient2 = UserFactory(role='patient')
    other_patient = PatientFactory(user=patient2)
    client = APIClient()
    client.force_authenticate(user=patient1)
    url = reverse('patient-detail', args=[other_patient.id])
    response = client.get(url)
    assert response.status_code == 403

def test_clinician_cannot_access_other_clinicians_patients():
    clinician1 = ClinicianFactory()
    clinician2 = ClinicianFactory()
    patient = PatientFactory(clinician=clinician2)
    client = APIClient()
    client.force_authenticate(user=clinician1)
    url = reverse('patient-detail', args=[patient.id])
    response = client.get(url)
    assert response.status_code == 403