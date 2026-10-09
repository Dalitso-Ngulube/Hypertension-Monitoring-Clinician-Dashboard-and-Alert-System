import pytest

from analytics.risk_assessment_service import (
    WHORiskScore,
    get_risk_profile,
    get_risk_recommendations,
)
from tests.factories import (
    BPReadingFactory,
    PatientFactory,
    PatientMedicalHistoryFactory,
)

pytestmark = pytest.mark.django_db

class TestWHORiskScore:
    def test_no_readings_returns_insufficient_data(self):
        patient = PatientFactory()
        risk, category, color, bmi_info = WHORiskScore.calculate(patient, None)
        assert risk is None
        assert category is None
        assert color == 'info'
        assert bmi_info['source'] == 'default'

    def test_profile_without_readings_returns_incomplete_profile(self):
        profile = get_risk_profile(PatientFactory())
        assert profile['risk_percentage'] is None
        assert profile['risk_category'] is None
        assert profile['is_complete'] is False

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

    def test_bmi_is_computed_when_history_has_no_bmi(self):
        patient = PatientFactory(height=2, weight=100)
        BPReadingFactory(patient=patient, systolic=120, diastolic=75)
        history = PatientMedicalHistoryFactory(patient=patient, bmi=None)

        _, _, _, bmi_info = WHORiskScore.calculate(patient, history)

        assert bmi_info == {
            'value': 25.0,
            'category': 'Overweight',
            'source': 'computed',
        }

    def test_profile_without_history_marks_default_bmi_incomplete(self):
        patient = PatientFactory(height=None, weight=None)
        BPReadingFactory(patient=patient, systolic=115, diastolic=75)

        profile = get_risk_profile(patient)

        assert profile['risk_percentage'] is not None
        assert profile['is_complete'] is False
        assert profile['bmi']['source'] == 'default'

    def test_profile_adds_risk_and_modifiable_factors(self):
        patient = PatientFactory(height=None, weight=None)
        BPReadingFactory(patient=patient, systolic=155, diastolic=95)
        PatientMedicalHistoryFactory(
            patient=patient,
            bmi=31,
            smoking_status='CURRENT',
            alcohol_consumption='HEAVY',
            physical_activity='SEDENTARY',
            diet_description='High sodium diet',
            has_kidney_disease=True,
            has_heart_disease=True,
            has_stroke_history=True,
            family_history_hypertension=True,
            family_history_diabetes=True,
            family_history_heart_disease=True,
        )

        profile = get_risk_profile(patient)

        assert 'Chronic Kidney Disease' in profile['additional_risk_factors']
        assert 'Current Smoker' in profile['additional_risk_factors']
        assert 'Smoking Cessation' in profile['modifiable_risk_factors']
        assert 'Weight Management (target BMI <25)' in profile['modifiable_risk_factors']
        assert any('Weight loss' in item for item in profile['recommendations'])


@pytest.mark.parametrize('category,expected', [
    ('Very High', '[URGENT]'),
    ('High', '[MEDICATION]'),
    ('Moderate', '[FOLLOW-UP]'),
    ('Low-Moderate', '[LIFESTYLE]'),
    ('Low', '[FOLLOW-UP]'),
])
def test_recommendations_cover_each_risk_category(category, expected):
    recs = get_risk_recommendations(category, [], [], {'category': 'Normal'})
    assert any(item.startswith(expected) for item in recs)
