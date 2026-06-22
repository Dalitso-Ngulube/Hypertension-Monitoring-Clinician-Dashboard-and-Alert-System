import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from tests.factories import PatientFactory, ClinicianFactory, BPReadingFactory

pytestmark = pytest.mark.django_db

class TestPatientTrendView:
    def test_returns_readings_ordered(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        reading1 = BPReadingFactory(patient=patient, recorded_at=timezone.now() - timedelta(days=2))
        reading2 = BPReadingFactory(patient=patient, recorded_at=timezone.now())
        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse('patient-trend', args=[patient.id])
        response = client.get(url)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        # Check ordering (oldest first as per view)
        assert data[0]['date'] < data[1]['date']

class TestRiskScoreView:
    def test_calculate_risk_score_based_on_recent_readings(self):
        clinician = ClinicianFactory()
        patient = PatientFactory(clinician=clinician)
        # Create 5 crisis readings and 5 stage2
        for _ in range(5):
            BPReadingFactory(patient=patient, systolic=190, diastolic=110, risk_category="CRISIS")
        for _ in range(5):
            BPReadingFactory(patient=patient, systolic=145, diastolic=95, risk_category="STAGE_2")
        client = APIClient()
        client.force_authenticate(user=clinician)
        url = reverse('risk-score', args=[patient.id])
        response = client.get(url)
        assert response.status_code == 200
        # Score = 5*10 + 5*5 = 75
        assert response.json()['score'] == 75
        assert response.json()['level'] == 'High'