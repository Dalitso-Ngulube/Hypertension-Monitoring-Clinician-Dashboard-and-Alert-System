import pytest
from unittest.mock import patch
from django.urls import reverse
from bp_readings.models import BPReading
from rest_framework.test import APIClient

from alerts.models import Alert
from tests.factories import (
    AdminFactory,
    BPReadingFactory,
    ClinicianFactory,
    PatientFactory,
    UserFactory,
)

pytestmark = pytest.mark.django_db

class TestBPReadingListCreate:
    def test_patient_list_is_limited_to_own_recent_readings_and_filter(self):
        user = UserFactory(role='patient')
        own = PatientFactory(user=user)
        other = PatientFactory()
        own_reading = BPReadingFactory(patient=own)
        BPReadingFactory(patient=other)
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get(
            reverse('bp-reading-list-create'), {'patient': own.id}
        )

        assert response.status_code == 200
        assert response.data['count'] == 1
        assert response.data['results'][0]['id'] == own_reading.id

    def test_admin_can_create_reading_for_any_patient(self):
        admin = AdminFactory()
        patient = PatientFactory()
        client = APIClient()
        client.force_authenticate(user=admin)

        response = client.post(reverse('bp-reading-list-create'), {
            'patient': patient.id,
            'systolic': 125,
            'diastolic': 75,
            'source': 'MANUAL',
        })

        assert response.status_code == 201

    def test_create_crisis_reading_triggers_alert(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        client = APIClient(raise_request_exception=False)
        client.force_authenticate(user=clinician)
        url = reverse('bp-reading-list-create')
        data = {
            'patient': patient.id,
            'systolic': 190,
            'diastolic': 110,
            'pulse_rate': 85,
            'source': 'MANUAL',
            'recorded_at': '2026-06-23T10:00:00Z'   # Provide a valid datetime
        }
        response = client.post(url, data)
        assert response.status_code == 201
        assert Alert.objects.filter(patient=patient, severity='CRITICAL').exists()

    def test_clinician_cannot_add_reading_for_other_patient(self):
        clinician = ClinicianFactory()
        other_clinician = ClinicianFactory()
        patient = PatientFactory(clinician=other_clinician)
        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse('bp-reading-list-create')
        data = {
            'patient': patient.id,
            'systolic': 130,
            'diastolic': 85,
            'recorded_at': '2026-06-23T10:00:00Z'
        }
        response = client.post(url, data)
        assert response.status_code == 403

    def test_patient_cannot_create_reading_for_other_patient(self):
        patient_user = UserFactory(role='patient')
        own_patient = PatientFactory(user=patient_user)
        other_patient = PatientFactory()
        client = APIClient()
        client.force_authenticate(user=patient_user)
        url = reverse('bp-reading-list-create')
        data = {
            'patient': other_patient.id,
            'systolic': 130,
            'diastolic': 85,
            'recorded_at': '2026-06-23T10:00:00Z'
        }
        response = client.post(url, data)
        assert response.status_code == 403

    def test_patient_add_endpoint_creates_own_reading(self):
        user = UserFactory(role='patient')
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(reverse('patient-add-reading'), {
            'systolic': 135,
            'diastolic': 85,
            'pulse_rate': 70,
        }, format='json')

        assert response.status_code == 201
        assert user.patient.filter(bp_readings__systolic=135).exists()

    def test_non_patient_cannot_use_patient_add_endpoint(self):
        clinician = ClinicianFactory()
        client = APIClient()
        client.force_authenticate(user=clinician)

        response = client.post(reverse('patient-add-reading'), {
            'systolic': 135,
            'diastolic': 85,
        }, format='json')

        assert response.status_code == 403

    def test_clinician_cannot_reassign_reading_to_other_clinicians_patient(self):
        clinician_a = ClinicianFactory()
        clinician_b = ClinicianFactory()
        patient_a = PatientFactory(clinician=clinician_a)
        patient_b = PatientFactory(clinician=clinician_b)
        reading = BPReadingFactory(patient=patient_a)
        client = APIClient()
        client.force_authenticate(user=clinician_a)

        response = client.patch(
            reverse('bp-reading-detail', args=[reading.id]),
            {'patient': patient_b.id},
            format='json',
        )

        reading.refresh_from_db()
        assert response.status_code == 400
        assert reading.patient == patient_a

    def test_patient_cannot_reassign_own_reading(self):
        user = UserFactory(role='patient')
        own_patient = PatientFactory(user=user)
        other_patient = PatientFactory()
        reading = BPReadingFactory(patient=own_patient)
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.patch(
            reverse('bp-reading-detail', args=[reading.id]),
            {'patient': other_patient.id},
            format='json',
        )

        reading.refresh_from_db()
        assert response.status_code in (400, 403)
        assert reading.patient == own_patient

    def test_updating_reading_to_crisis_creates_alert(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        reading = BPReadingFactory(
            patient=patient, systolic=115, diastolic=75
        )
        client = APIClient()
        client.force_authenticate(user=clinician)

        response = client.patch(
            reverse('bp-reading-detail', args=[reading.id]),
            {'systolic': 190, 'diastolic': 125},
            format='json',
        )

        reading.refresh_from_db()
        assert response.status_code == 200
        assert reading.risk_category == 'CRISIS'
        assert Alert.objects.filter(
            reading=reading, alert_type='CRISIS', is_resolved=False
        ).exists()

    def test_updating_crisis_reading_to_normal_resolves_alert(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        reading = BPReadingFactory(
            patient=patient, systolic=190, diastolic=125
        )
        alert = Alert.objects.get(reading=reading, alert_type='CRISIS')
        client = APIClient()
        client.force_authenticate(user=clinician)

        response = client.patch(
            reverse('bp-reading-detail', args=[reading.id]),
            {'systolic': 110, 'diastolic': 70},
            format='json',
        )

        alert.refresh_from_db()
        assert response.status_code == 200
        assert Alert.objects.filter(pk=alert.pk).exists()
        assert alert.is_resolved is True
        assert alert.resolved_at is not None

    def test_resaving_reading_does_not_duplicate_alerts(self):
        reading = BPReadingFactory(systolic=190, diastolic=125)
        reading.save()

        assert Alert.objects.filter(
            reading=reading, alert_type='CRISIS', is_resolved=False
        ).count() == 1

    @patch(
        'alerts.services.Alert.objects.create',
        side_effect=Exception('forced alert failure'),
    )
    def test_reading_rolls_back_when_alert_creation_fails(self, _create_alert):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        client = APIClient(raise_request_exception=False)
        client.force_authenticate(user=clinician)

        response = client.post(reverse('bp-reading-list-create'), {
            'patient': patient.id,
            'systolic': 190,
            'diastolic': 125,
            'source': 'MANUAL',
        }, format='json', HTTP_HOST='testserver')

        assert response.status_code == 500
        assert not BPReading.objects.filter(
            patient=patient, systolic=190, diastolic=125
        ).exists()
