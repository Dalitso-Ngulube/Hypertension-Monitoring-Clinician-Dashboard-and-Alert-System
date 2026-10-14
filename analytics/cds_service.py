"""
CDS Service — non-validated demonstration; not for clinical use.

This module produces a stage assessment and non-prescriptive monitoring
guidance based on recent blood pressure readings. It does not issue
treatment or prescribing instructions. Any decision on pharmacological
management rests with the treating clinician, guided by the applicable
national or international guideline.

The classifier used elsewhere in this system follows the ACC/AHA 2017
thresholds. The stage labels produced here are aligned to that classifier.
"""

from datetime import timedelta

from django.db.models import Avg
from django.utils import timezone

from bp_readings.models import BPReading


def get_recent_avg_bp(patient, days=30):
    """Return average systolic and diastolic over the last `days` days."""
    cutoff = timezone.now() - timedelta(days=days)
    readings = BPReading.objects.filter(
        patient=patient,
        recorded_at__gte=cutoff
    )
    avg_sys = readings.aggregate(Avg('systolic'))['systolic__avg']
    avg_dia = readings.aggregate(Avg('diastolic'))['diastolic__avg']
    return avg_sys, avg_dia


def get_latest_reading(patient):
    """Return the most recent BP reading."""
    return patient.bp_readings.order_by('-recorded_at').first()


def evaluate_hypertension_stage(avg_sys, avg_dia):
    """Return the stage based on average readings, aligned to AHA/ACC 2017."""
    if avg_sys is None or avg_dia is None:
        return None
    if avg_sys >= 180 or avg_dia >= 120:
        return 'CRISIS'
    if avg_sys >= 140 or avg_dia >= 90:
        return 'STAGE_2'
    if avg_sys >= 130 or avg_dia >= 80:
        return 'STAGE_1'
    if avg_sys >= 120:
        return 'ELEVATED'
    return 'NORMAL'


def get_monitoring_recommendations(patient, stage, comorbidities):
    """
    Return non-prescriptive monitoring guidance for the given stage.

    This function does not issue treatment instructions. It surfaces the
    stage assessment and general monitoring steps only.
    """
    guidance = []

    if stage == 'CRISIS':
        guidance.append({
            'priority': 'URGENT',
            'recommendation': (
                'Blood pressure is in the crisis range. Refer the patient '
                'for immediate clinical assessment.'
            ),
            'details': (
                'A hypertensive crisis requires urgent evaluation. Do not delay referral.'
            ),
        })
        return guidance

    if stage == 'STAGE_2':
        guidance.append({
            'priority': 'HIGH',
            'recommendation': (
                'Blood pressure is in Stage 2. Prompt clinical review is recommended.'
            ),
            'details': (
                'Treatment decisions rest with the treating clinician, '
                'guided by the applicable guideline and the patient profile.'
            ),
        })
    elif stage == 'STAGE_1':
        guidance.append({
            'priority': 'MEDIUM',
            'recommendation': (
                'Blood pressure is in Stage 1. Review the reading history '
                'and consider clinical assessment.'
            ),
            'details': (
                'Lifestyle modification and clinical review are appropriate; '
                'any treatment decision rests with the clinician.'
            ),
        })
    elif stage == 'ELEVATED':
        guidance.append({
            'priority': 'LOW',
            'recommendation': (
                'Blood pressure is elevated. Continue monitoring and reassess at the next visit.'
            ),
            'details': 'Encourage continued home readings to establish a trend.',
        })
    elif stage == 'NORMAL':
        guidance.append({
            'priority': 'LOW',
            'recommendation': 'Blood pressure is within the normal range.',
            'details': 'Continue routine monitoring.',
        })
    else:
        guidance.append({
            'priority': 'LOW',
            'recommendation': 'Insufficient data to assess stage.',
            'details': 'Obtain recent BP readings.',
        })

    # Flag relevant comorbidities for clinician awareness (no treatment advice).
    if comorbidities.get('diabetes'):
        guidance.append({
            'priority': 'INFO',
            'recommendation': 'Patient has a recorded diagnosis of diabetes.',
            'details': 'Relevant to cardiovascular risk assessment.',
        })
    if comorbidities.get('ckd'):
        guidance.append({
            'priority': 'INFO',
            'recommendation': 'Patient has a recorded diagnosis of chronic kidney disease.',
            'details': 'Relevant to cardiovascular risk assessment.',
        })

    return guidance


def get_lab_recommendations(patient, stage, comorbidities):
    """
    Suggest baseline and follow-up laboratory investigations.

    These are monitoring suggestions, not orders. The treating clinician
    decides which investigations to request.
    """
    labs = []
    if stage in ['STAGE_1', 'STAGE_2', 'CRISIS']:
        labs.append('Serum creatinine and eGFR')
        labs.append('Serum potassium')
        labs.append('Urinalysis (protein, blood)')
        labs.append('Fasting lipid panel')
        labs.append('Fasting blood glucose or HbA1c')
    if comorbidities.get('diabetes'):
        labs.append('HbA1c (every 3-6 months)')
        labs.append('Urine albumin-to-creatinine ratio')
    if comorbidities.get('ckd'):
        labs.append('Urine protein-to-creatinine ratio')
        labs.append('Calcium, phosphate, PTH if advanced CKD')
    if stage in ['STAGE_1', 'STAGE_2']:
        labs.append('Repeat electrolytes and creatinine 2-4 weeks after any medication change')
    return labs


def get_lifestyle_recommendations(patient, comorbidities):
    """Return lifestyle modification advice for the patient."""
    lifestyle = []
    try:
        history = patient.medical_history
    except AttributeError:
        history = None

    if history:
        if history.smoking_status == 'CURRENT':
            lifestyle.append('Smoking cessation: counsel and consider support options.')
        if history.alcohol_consumption in ['MODERATE', 'HEAVY']:
            lifestyle.append('Alcohol reduction: limit to ≤1 drink/day for women, ≤2 for men.')
        if history.physical_activity in ['SEDENTARY', 'LIGHT']:
            lifestyle.append('Physical activity: aim for at least 150 minutes of moderate-intensity aerobic activity per week.')
        if history.diet_description:
            lifestyle.append('Dietary improvement: DASH-style diet rich in fruits, vegetables, whole grains, low-fat dairy, and reduced sodium.')
        else:
            lifestyle.append('Dietary recommendations: consider DASH diet; limit sodium to <2,300 mg/day (ideal <1,500 mg).')
        if history.family_history_hypertension:
            lifestyle.append('Family history of hypertension: emphasise lifestyle measures and regular monitoring.')
    else:
        lifestyle.append('Smoking cessation, reduced alcohol intake, regular exercise, and a DASH-style diet are recommended.')
        lifestyle.append('Limit sodium intake to <2,300 mg/day.')

    return lifestyle


def get_clinical_summary(patient, stage, recommendations, labs, lifestyle):
    """Generate a human-readable summary. Non-validated demonstration."""
    summary = f"Patient {patient.first_name} {patient.last_name} (ID: {patient.id}) — BP Assessment\n"
    summary += f"Stage: {stage or 'Undetermined'}\n"
    summary += "Monitoring guidance:\n"
    for rec in recommendations:
        summary += f"  - {rec['recommendation']} (Priority: {rec['priority']})\n"
    summary += "\nSuggested investigations (clinician to confirm):\n"
    for lab in labs:
        summary += f"  - {lab}\n"
    summary += "\nLifestyle modifications:\n"
    for item in lifestyle:
        summary += f"  - {item}\n"
    return summary


def get_cds_recommendations(patient):
    """
    Main entry point: returns structured CDS data for a patient.

    This is a non-validated demonstration. It is not intended for
    clinical decision-making.
    """
    avg_sys, avg_dia = get_recent_avg_bp(patient, days=30)
    latest = get_latest_reading(patient)
    stage = evaluate_hypertension_stage(avg_sys, avg_dia)

    if stage is None:
        return {
            'error': 'No recent BP readings available for this patient.',
            'stage': None,
            'recommendations': [],
            'labs': [],
            'lifestyle': [],
            'summary': 'Insufficient data.',
        }

    comorbidities = {
        'diabetes': False,
        'ckd': False,
        'heart_failure': False,
        'heart_disease': False,
        'stroke': False,
    }
    try:
        history = patient.medical_history
        comorbidities['diabetes'] = history.has_diabetes
        comorbidities['ckd'] = history.has_kidney_disease
        comorbidities['heart_failure'] = history.has_heart_disease
        comorbidities['heart_disease'] = history.has_heart_disease
        comorbidities['stroke'] = history.has_stroke_history
    except AttributeError:
        pass

    monitoring = get_monitoring_recommendations(patient, stage, comorbidities)
    labs = get_lab_recommendations(patient, stage, comorbidities)
    lifestyle = get_lifestyle_recommendations(patient, comorbidities)
    summary = get_clinical_summary(patient, stage, monitoring, labs, lifestyle)

    current_meds = []
    try:
        history = patient.medical_history
        for med in history.current_medications.all():
            current_meds.append(med.name)
    except AttributeError:
        pass

    return {
        'stage': stage,
        'latest_reading': {
            'systolic': latest.systolic if latest else None,
            'diastolic': latest.diastolic if latest else None,
            'recorded_at': latest.recorded_at.isoformat() if latest else None,
        },
        'average_systolic': avg_sys,
        'average_diastolic': avg_dia,
        'current_medications': current_meds,
        'comorbidities': comorbidities,
        'recommendations': monitoring,
        'labs': labs,
        'lifestyle': lifestyle,
        'summary': summary,
    }
