from datetime import timedelta

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from tests.factories import (
    AdminFactory,
    AlertFactory,
    BPReadingFactory,
    ClinicianFactory,
    PatientFactory,
    UserFactory,
)

pytestmark = pytest.mark.django_db


class TestPatientTrendView:
    def test_returns_readings_ordered(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        BPReadingFactory(patient=patient)
        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse('patient-trend', args=[patient.id])
        response = client.get(url)
        assert response.status_code == 200

    def test_patient_can_read_own_trend_and_cannot_read_another(self):
        patient_user = UserFactory(role='patient')
        other_user = UserFactory(role='patient')
        patient = PatientFactory(user=patient_user)
        other_patient = PatientFactory(user=other_user)
        client = APIClient()
        client.force_authenticate(user=patient_user)

        own_response = client.get(reverse('patient-trend', args=[patient.id]))
        other_response = client.get(
            reverse('patient-trend', args=[other_patient.id])
        )

        assert own_response.status_code == 200
        assert other_response.status_code == 404


class TestRiskScoreView:
    def test_risk_score_for_no_readings_is_low(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        client = APIClient()
        client.force_authenticate(user=clinician)

        response = client.get(reverse('risk-score', args=[patient.id]))

        assert response.data == {'score': 0, 'level': 'Low'}

    def test_admin_can_view_summary_and_risk_distribution(self):
        admin = AdminFactory()
        patient = PatientFactory()
        BPReadingFactory(patient=patient, systolic=190, diastolic=125)
        client = APIClient()
        client.force_authenticate(user=admin)

        summary = client.get(reverse('analytics-summary'))
        distribution = client.get(reverse('risk-distribution'))

        assert summary.data['total_patients'] >= 1
        assert summary.data['critical_readings'] >= 1
        assert 'CRISIS' in distribution.data

    def test_calculate_risk_score(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        BPReadingFactory(patient=patient, systolic=190, diastolic=110, risk_category='CRISIS')
        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse('risk-score', args=[patient.id])
        response = client.get(url)
        assert response.status_code == 200
        assert 'score' in response.data

    def test_bp_trend_view(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        BPReadingFactory(patient=patient, systolic=120, diastolic=80)
        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse('bp-trend', args=[patient.id])
        response = client.get(url, {'days': 30})
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert 'avg_systolic' in data[0]

    def test_time_patterns_return_each_time_slot(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        BPReadingFactory(patient=patient, systolic=130, diastolic=80)
        client = APIClient()
        client.force_authenticate(user=clinician)

        response = client.get(reverse('time-patterns', args=[patient.id]))

        assert response.status_code == 200
        assert set(response.data) == {'night', 'morning', 'afternoon', 'evening'}
        assert sum(slot['count'] for slot in response.data.values()) == 1

    def test_analytics_summary_view(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        BPReadingFactory(patient=patient)
        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse('analytics-summary')
        response = client.get(url)
        assert response.status_code == 200
        assert 'total_patients' in response.data

    def test_risk_distribution_view(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        BPReadingFactory(patient=patient, systolic=110, diastolic=70)   # NORMAL
        BPReadingFactory(patient=patient, systolic=125, diastolic=75)   # ELEVATED
        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse('risk-distribution')
        response = client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert 'NORMAL' in data
        assert 'ELEVATED' in data

    def test_export_patient_csv(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        BPReadingFactory(patient=patient, systolic=120, diastolic=80)
        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse('export-patient-csv', args=[patient.id])
        response = client.get(url)
        assert response.status_code == 200
        assert response['Content-Type'] == 'text/csv'
        assert 'attachment' in response['Content-Disposition']

    def test_export_patient_csv_includes_alert_and_no_alert_rows(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician, gender=None)
        reading_with_alert = BPReadingFactory(
            patient=patient, systolic=190, diastolic=125, pulse_rate=None
        )
        AlertFactory(
            patient=patient,
            created_at=reading_with_alert.recorded_at,
            severity='CRITICAL',
            message='Emergency',
        )
        older_reading = BPReadingFactory(
            patient=patient, systolic=120, diastolic=75
        )
        type(older_reading).objects.filter(pk=older_reading.pk).update(
            recorded_at=older_reading.recorded_at - timedelta(days=2)
        )
        client = APIClient()
        client.force_authenticate(user=clinician)

        response = client.get(reverse('export-patient-csv', args=[patient.id]))
        content = response.content.decode()

        assert 'Emergency' in content
        assert 'No alert' in content
        assert 'N/A' in content

    def test_export_summary_csv(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse('export-summary-csv')
        response = client.get(url)
        assert response.status_code == 200
        assert response['Content-Type'] == 'text/csv'
        assert 'attachment' in response['Content-Disposition']

    def test_admin_export_summary_includes_patient_without_readings(self):
        admin = AdminFactory()
        PatientFactory(user=UserFactory(role='admin'), gender=None)
        client = APIClient()
        client.force_authenticate(user=admin)

        response = client.get(reverse('export-summary-csv'))
        content = response.content.decode()

        assert response.status_code == 200
        assert 'No readings' in content

    def test_patient_is_forbidden_from_csv_exports(self):
        patient_user = UserFactory(role='patient')
        patient = PatientFactory(user=patient_user)
        client = APIClient()
        client.force_authenticate(user=patient_user)

        patient_export = client.get(
            reverse('export-patient-csv', args=[patient.id])
        )
        summary_export = client.get(reverse('export-summary-csv'))

        assert patient_export.status_code == 403
        assert summary_export.status_code == 403

    def test_cds_view(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        BPReadingFactory(patient=patient, systolic=145, diastolic=92)
        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse('clinical-decision-support', args=[patient.id])
        response = client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert 'stage' in data
        assert 'recommendations' in data