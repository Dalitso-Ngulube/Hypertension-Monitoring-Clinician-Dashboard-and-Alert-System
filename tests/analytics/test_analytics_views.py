import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from tests.factories import BPReadingFactory, ClinicianFactory, PatientFactory

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


class TestRiskScoreView:
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