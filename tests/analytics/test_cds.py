import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from analytics.cds_service import (
    get_cds_recommendations,
    get_lab_recommendations,
    get_lifestyle_recommendations,
    get_medication_recommendations,
)
from tests.factories import (
    BPReadingFactory,
    ClinicianFactory,
    PatientFactory,
    PatientMedicalHistoryFactory,
)

pytestmark = pytest.mark.django_db


class TestCDS:
    def test_get_cds_recommendations(self):
        patient = PatientFactory(age=55, gender='M')
        BPReadingFactory(patient=patient, systolic=145, diastolic=92)
        PatientMedicalHistoryFactory(patient=patient, smoking_status='CURRENT')
        data = get_cds_recommendations(patient)
        assert 'stage' in data
        assert 'recommendations' in data
        assert 'labs' in data
        assert 'lifestyle' in data

    def test_get_medication_recommendations_stage1(self):
        patient = PatientFactory()
        recs = get_medication_recommendations(patient, 'STAGE_1', {})
        assert len(recs) > 0
        assert any('monotherapy' in r['recommendation'].lower() for r in recs)

    def test_get_lifestyle_recommendations_smoker(self):
        patient = PatientFactory()
        history = PatientMedicalHistoryFactory(patient=patient, smoking_status='CURRENT')
        lifestyle = get_lifestyle_recommendations(patient, history)
        assert any('smoking' in item.lower() for item in lifestyle)

    def test_get_lab_recommendations_diabetic(self):
        labs = get_lab_recommendations(None, 'STAGE_2', {'diabetes': True})
        assert any('HbA1c' in lab for lab in labs)

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