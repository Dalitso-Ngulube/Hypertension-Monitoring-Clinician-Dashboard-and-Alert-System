import pytest
from analytics.risk_assessment_service import WHORiskScore
from tests.factories import PatientFactory, PatientMedicalHistoryFactory, BPReadingFactory

pytestmark = pytest.mark.django_db

class TestWHORiskScore:
    def test_male_normal_risk(self):
        patient = PatientFactory(age=45, gender='M')
        BPReadingFactory(patient=patient, systolic=120, diastolic=80)
        history = PatientMedicalHistoryFactory(
            patient=patient,
            bmi=24.0,
            smoking_status='NEVER',
            has_diabetes=False
        )
        risk, category, color, bmi_info = WHORiskScore.calculate(patient, history)
        assert risk is not None
        assert category in ['Low', 'Low-Moderate', 'Moderate', 'High', 'Very High']

    def test_edge_systolic_180(self):
        patient = PatientFactory(age=50, gender='M')
        BPReadingFactory(patient=patient, systolic=180, diastolic=100)
        history = PatientMedicalHistoryFactory(
            patient=patient,
            bmi=25.0,
            smoking_status='NEVER',
            has_diabetes=False
        )
        risk, category, color, bmi_info = WHORiskScore.calculate(patient, history)
        assert category == 'High'
    def test_female_normal_risk(self):
        patient = PatientFactory(age=35, gender='F')
        BPReadingFactory(patient=patient, systolic=110, diastolic=70)
        history = PatientMedicalHistoryFactory(patient=patient, bmi=22.0, smoking_status='NEVER')
        risk, category, color, bmi_info = WHORiskScore.calculate(patient, history)
        assert category in ['Low', 'Low-Moderate']

    def test_male_smoker_diabetic(self):
        patient = PatientFactory(age=60, gender='M')
        BPReadingFactory(patient=patient, systolic=155, diastolic=95)
        history = PatientMedicalHistoryFactory(
            patient=patient,
            bmi=28.0,
            smoking_status='CURRENT',
            has_diabetes=True
        )
        risk, category, color, bmi_info = WHORiskScore.calculate(patient, history)
        assert category in ['High', 'Very High']

    def test_obese_bmi(self):
        patient = PatientFactory(age=50, gender='M')
        BPReadingFactory(patient=patient, systolic=130, diastolic=85)
        history = PatientMedicalHistoryFactory(patient=patient, bmi=33.0, smoking_status='NEVER')
        risk, category, color, bmi_info = WHORiskScore.calculate(patient, history)
        assert bmi_info['category'] == 'Obese'

    def test_missing_bmi_default(self):
        patient = PatientFactory(age=45, gender='M', height=None, weight=None)
        BPReadingFactory(patient=patient, systolic=120, diastolic=80)
        history = PatientMedicalHistoryFactory(patient=patient, bmi=None)
        risk, category, color, bmi_info = WHORiskScore.calculate(patient, history)
        assert bmi_info['source'] == 'default'
        assert bmi_info['value'] == 24.0
