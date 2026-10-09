import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from patients.models import Allergy, MedicalCondition, Medication, Patient
from tests.factories import (
    AdminFactory,
    ClinicianFactory,
    PatientFactory,
    UserFactory,
)

pytestmark = pytest.mark.django_db


class TestPatientListCreateView:
    def test_patient_sees_only_own_patients(self):
        patient_user = UserFactory(role='patient')
        other_user = UserFactory(role='patient')

        client = APIClient()
        client.force_authenticate(user=patient_user)
        url = reverse('patient-list-create')
        response = client.get(url)
        assert response.status_code == 200
        assert response.data['count'] == 1
        assert response.data['results'][0]['user'] == patient_user.id
        assert response.data['results'][0]['user'] != other_user.id

    def test_admin_sees_all_patients(self):
        admin = AdminFactory()
        PatientFactory(user=UserFactory(role='admin'))
        PatientFactory(user=UserFactory(role='admin'))
        client = APIClient()
        client.force_authenticate(user=admin)

        response = client.get(reverse('patient-list-create'))

        assert response.status_code == 200
        assert response.data['count'] == 2

    def test_clinician_creates_patient_assigned_to_self(self):
        clinician = ClinicianFactory()
        client = APIClient()
        client.force_authenticate(user=clinician)

        response = client.post(reverse('patient-list-create'), {
            'first_name': 'New',
            'last_name': 'Patient',
            'age': 42,
        })

        assert response.status_code == 201
        patient = Patient.objects.get(pk=response.data['id'])
        assert patient.clinician == clinician

    def test_patient_cannot_create_patient_record(self):
        patient_user = UserFactory(role='patient')
        client = APIClient()
        client.force_authenticate(user=patient_user)

        response = client.post(reverse('patient-list-create'), {
            'first_name': 'Not',
            'last_name': 'Allowed',
            'age': 35,
        })

        assert response.status_code == 403

    def test_list_requires_authentication(self):
        response = APIClient().get(reverse('patient-list-create'))
        assert response.status_code == 403

    def test_clinician_sees_assigned_patients(self):
        clinician = ClinicianFactory()
        assigned = PatientFactory(clinician=clinician)
        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse('patient-list-create')
        response = client.get(url)
        assert response.status_code == 200
        assert response.data['count'] == 1
        assert response.data['results'][0]['id'] == assigned.id


class TestPatientDetailView:
    def test_patient_cannot_access_other_patients(self):
        patient_user = UserFactory(role='patient')
        other_user = UserFactory(role='patient')
        other_patient = PatientFactory(user=other_user)
        client = APIClient()
        client.force_authenticate(user=patient_user)
        url = reverse('patient-detail', args=[other_patient.id])
        response = client.get(url)
        assert response.status_code == 403

    def test_clinician_can_retrieve_update_and_delete_assigned_patient(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse('patient-detail', args=[patient.id])

        retrieved = client.get(url)
        updated = client.patch(url, {'first_name': 'Updated'})
        deleted = client.delete(url)

        assert retrieved.status_code == 200
        assert updated.status_code == 200
        assert updated.data['first_name'] == 'Updated'
        assert deleted.status_code == 204

    def test_missing_patient_returns_404(self):
        clinician = ClinicianFactory()
        client = APIClient()
        client.force_authenticate(user=clinician)

        response = client.get(reverse('patient-detail', args=[999999]))

        assert response.status_code == 404

    def test_patient_medical_history_get(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse(
            'patient-medical-history', kwargs={'patient_id': patient.id}
        )
        response = client.get(url)
        assert response.status_code == 200
        assert 'smoking_status' in response.data

    def test_medical_history_patch_updates_scalar_and_relationship_fields(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        condition = MedicalCondition.objects.create(name='Hypertension')
        allergy = Allergy.objects.create(name='Pollen')
        medication = Medication.objects.create(name='Example medication')
        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse(
            'patient-medical-history', kwargs={'patient_id': patient.id}
        )

        response = client.patch(url, {
            'smoking_status': 'FORMER',
            'condition_ids': [condition.id],
            'allergy_ids': [allergy.id],
            'medication_ids': [medication.id],
        }, format='json')

        assert response.status_code == 200
        assert response.data['smoking_status'] == 'FORMER'
        assert response.data['conditions'][0]['id'] == condition.id
        assert response.data['allergies'][0]['id'] == allergy.id
        assert response.data['current_medications'][0]['id'] == medication.id

    def test_medical_history_unknown_patient_returns_404(self):
        clinician = ClinicianFactory()
        client = APIClient()
        client.force_authenticate(user=clinician)

        url = reverse(
            'patient-medical-history', kwargs={'patient_id': 999999}
        )
        response = client.get(url)

        assert response.status_code == 404


class TestReferenceDataViews:
    @pytest.mark.parametrize('url_name', [
        'medical-conditions',
        'allergies',
        'medications',
    ])
    def test_reference_lists_require_clinician_or_admin(self, url_name):
        patient_user = UserFactory(role='patient')
        client = APIClient()
        client.force_authenticate(user=patient_user)

        response = client.get(reverse(url_name))

        assert response.status_code == 403

    def test_clinician_can_create_reference_data(self):
        clinician = ClinicianFactory()
        client = APIClient()
        client.force_authenticate(user=clinician)

        response = client.post(reverse('medical-conditions'), {
            'name': 'Asthma',
            'category': 'RESPIRATORY',
            'description': 'A respiratory condition',
        }, format='json')

        assert response.status_code == 201
        assert response.data['name'] == 'Asthma'
