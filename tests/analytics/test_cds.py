from datetime import timedelta

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from analytics.cds_service import (
    evaluate_hypertension_stage,
    get_cds_recommendations,
    get_clinical_summary,
    get_lab_recommendations,
    get_lifestyle_recommendations,
    get_monitoring_recommendations,
    get_recent_avg_bp,
)
from tests.factories import (
    BPReadingFactory,
    ClinicianFactory,
    PatientFactory,
    PatientMedicalHistoryFactory,
)

pytestmark = pytest.mark.django_db


class TestCDS:
    def test_no_readings_returns_insufficient_data(self):
        patient = PatientFactory()

        data = get_cds_recommendations(patient)

        assert data['stage'] is None
        assert data['error'] == 'No recent BP readings available for this patient.'

    @pytest.mark.parametrize('systolic,diastolic,stage', [
        (None, 80, None),
        (180, 80, 'CRISIS'),
        (140, 80, 'STAGE_2'),
        (130, 80, 'STAGE_1'),
        (120, 70, 'ELEVATED'),
        (119, 79, 'NORMAL'),
    ])
    def test_evaluate_hypertension_stage_boundaries(
        self, systolic, diastolic, stage
    ):
        assert evaluate_hypertension_stage(systolic, diastolic) == stage

    def test_recent_average_ignores_old_readings(self):
        patient = PatientFactory()
        recent = BPReadingFactory(patient=patient, systolic=140, diastolic=90)
        BPReadingFactory(patient=patient, systolic=200, diastolic=120)
        type(recent).objects.filter(pk=recent.pk).update(
            recorded_at=recent.recorded_at - timedelta(days=40)
        )

        avg_sys, avg_dia = get_recent_avg_bp(patient)

        assert avg_sys == 200
        assert avg_dia == 120

    def test_get_cds_recommendations(self):
        patient = PatientFactory(age=55, gender='M')
        BPReadingFactory(patient=patient, systolic=145, diastolic=92)
        PatientMedicalHistoryFactory(patient=patient, smoking_status='CURRENT')
        data = get_cds_recommendations(patient)
        assert 'stage' in data
        assert 'recommendations' in data
        assert 'labs' in data
        assert 'lifestyle' in data

    def test_get_monitoring_recommendations_stage1(self):
        patient = PatientFactory()
        recs = get_monitoring_recommendations(patient, 'STAGE_1', {})
        assert len(recs) > 0
        assert any(
            'Stage 1' in r['recommendation'] or
            'clinical assessment' in r['recommendation']
            for r in recs
        )

    def test_monitoring_recommendations_crisis_and_comorbidities(self):
        patient = PatientFactory()
        crisis = get_monitoring_recommendations(patient, 'CRISIS', {})
        stage_two = get_monitoring_recommendations(
            patient, 'STAGE_2', {'diabetes': True}
        )

        assert crisis[0]['priority'] == 'URGENT'
        assert 'immediate clinical assessment' in crisis[0]['recommendation']
        assert 'Initiate' not in stage_two[0]['recommendation']
        assert 'ACE inhibitor' not in stage_two[0]['recommendation']
        assert any('diabetes' in r['recommendation'].lower() for r in stage_two)

    def test_monitoring_recommendations_contain_no_drug_names(self):
        """The CDS module must not issue prescribing instructions."""
        patient = PatientFactory()
        forbidden = (
            'initiate', 'statin', 'aspirin', 'ace inhibitor', 'arb',
            'thiazide', 'ccb', 'monotherapy', 'dual therapy',
        )
        for stage in ('NORMAL', 'ELEVATED', 'STAGE_1', 'STAGE_2', 'CRISIS'):
            recs = get_monitoring_recommendations(patient, stage, {})
            for rec in recs:
                text = rec['recommendation'].lower()
                assert not any(term in text for term in forbidden), (
                    f"Prescribing text found in {stage}: {rec['recommendation']}"
                )

    def test_labs_include_comorbidity_followups(self):
        labs = get_lab_recommendations(
            None, 'STAGE_1', {'diabetes': True, 'ckd': True}
        )

        assert any('HbA1c' in lab for lab in labs)
        assert any('protein-to-creatinine' in lab for lab in labs)

    def test_get_lifestyle_recommendations_smoker(self):
        patient = PatientFactory()
        history = PatientMedicalHistoryFactory(patient=patient, smoking_status='CURRENT')
        lifestyle = get_lifestyle_recommendations(patient, history)
        assert any('smoking' in item.lower() for item in lifestyle)

    def test_lifestyle_without_history_returns_generic_advice(self):
        patient = PatientFactory()

        lifestyle = get_lifestyle_recommendations(patient, {})

        assert any('DASH' in item for item in lifestyle)
        assert any('sodium' in item for item in lifestyle)

    def test_clinical_summary_formats_lists(self):
        patient = PatientFactory(first_name='Sam', last_name='Sample')

        summary = get_clinical_summary(
            patient,
            None,
            [{'recommendation': 'Monitor BP', 'priority': 'LOW'}],
            ['Potassium'],
            ['Exercise'],
        )

        assert 'Sam Sample' in summary
        assert 'Stage: Undetermined' in summary
        assert 'Monitor BP (Priority: LOW)' in summary

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