# analytics/cds_service.py

from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Avg
from patients.models import Patient, PatientMedicalHistory
from bp_readings.models import BPReading
from alerts.models import Alert
from core.utils import classify_bp

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
    """Return the stage based on average readings."""
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

def get_medication_recommendations(patient, stage, comorbidities):
    """
    Return medication recommendations based on stage and comorbidities.
    Following JNC 8 guidelines.
    """
    recommendations = []

    # Base recommendations by stage
    if stage == 'CRISIS':
        recommendations.append({
            'priority': 'URGENT',
            'recommendation': 'Immediate referral to emergency department. Do not delay.',
            'details': 'Hypertensive crisis requires urgent intravenous antihypertensive therapy and monitoring.'
        })
        return recommendations

    # Comorbidity-based preferences
    preferred_classes = []
    avoid_classes = []

    # ACE inhibitors or ARBs preferred for diabetes, CKD, heart failure
    if comorbidities.get('diabetes') or comorbidities.get('ckd') or comorbidities.get('heart_failure'):
        preferred_classes.extend(['ACE inhibitor', 'ARB'])
    # Thiazide diuretics or CCBs for Black patients (we don't track race yet, so we'll skip)

    if stage == 'STAGE_2':
        # Dual therapy
        if preferred_classes:
            first = preferred_classes[0]
            second = 'Thiazide diuretic' if first != 'Thiazide diuretic' else 'CCB'
            recommendations.append({
                'priority': 'HIGH',
                'recommendation': f'Initiate dual therapy: {first} + {second}.',
                'details': f'Consider combination therapy to achieve target BP (<140/90, or <130/80 if diabetic/CKD).'
            })
        else:
            recommendations.append({
                'priority': 'HIGH',
                'recommendation': 'Initiate dual therapy: Thiazide + ACE inhibitor/ARB/CCB.',
                'details': 'Consider combination therapy to achieve target BP (<140/90).'
            })
        # Add note on intensification
        recommendations.append({
            'priority': 'MEDIUM',
            'recommendation': 'If BP remains uncontrolled, consider adding a third agent or increasing doses.',
            'details': 'Monitor for side effects and adjust according to response.'
        })

    elif stage == 'STAGE_1':
        if preferred_classes:
            rec = {
                'priority': 'MEDIUM',
                'recommendation': f'Initiate monotherapy: {preferred_classes[0]}.',
                'details': f'Start with low dose, titrate up. Target BP <140/90 (or <130/80 if diabetic/CKD).'
            }
            recommendations.append(rec)
        else:
            recommendations.append({
                'priority': 'MEDIUM',
                'recommendation': 'Initiate monotherapy: Thiazide, ACE inhibitor, ARB, or CCB.',
                'details': 'Choose based on patient profile. Target BP <140/90.'
            })
        recommendations.append({
            'priority': 'LOW',
            'recommendation': 'Consider lifestyle modifications before adding medication.',
            'details': 'Weight loss, DASH diet, sodium restriction, exercise, smoking cessation.'
        })

    elif stage == 'ELEVATED':
        recommendations.append({
            'priority': 'LOW',
            'recommendation': 'Lifestyle modifications are first-line.',
            'details': 'Weight reduction, dietary changes (DASH), physical activity, reduced sodium intake.'
        })
        recommendations.append({
            'priority': 'LOW',
            'recommendation': 'Reassess BP in 3-6 months.',
            'details': 'If BP remains elevated, consider medication initiation.'
        })

    elif stage == 'NORMAL':
        recommendations.append({
            'priority': 'LOW',
            'recommendation': 'BP is within normal range. Continue lifestyle measures.',
            'details': 'Reassess annually or as clinically indicated.'
        })

    else:
        recommendations.append({
            'priority': 'LOW',
            'recommendation': 'Insufficient data to assess stage.',
            'details': 'Please obtain recent BP readings.'
        })

    return recommendations

def get_lab_recommendations(patient, stage, comorbidities):
    """
    Suggest baseline and follow-up laboratory investigations.
    """
    labs = []
    if stage in ['STAGE_1', 'STAGE_2', 'CRISIS']:
        labs.append('Baseline serum creatinine and eGFR')
        labs.append('Serum potassium')
        labs.append('Urinalysis (protein, blood)')
        labs.append('Fasting lipid panel')
        labs.append('Fasting blood glucose or HbA1c')
    if comorbidities.get('diabetes'):
        labs.append('HbA1c (every 3-6 months)')
        labs.append('Microalbuminuria (urine albumin-to-creatinine ratio)')
    if comorbidities.get('ckd'):
        labs.append('Urine protein-to-creatinine ratio')
        labs.append('Calcium, phosphate, PTH if advanced CKD')
    # If on diuretics or ACE inhibitors, consider monitoring potassium and creatinine in 2-4 weeks.
    if stage in ['STAGE_1', 'STAGE_2']:
        labs.append('Repeat electrolytes and creatinine in 2-4 weeks after starting/up-titrating medications')
    return labs

def get_lifestyle_recommendations(patient, comorbidities):
    """Return lifestyle modification advice."""
    lifestyle = []
    # Based on patient's medical history, we can tailor
    try:
        history = patient.medical_history
        if history.smoking_status == 'CURRENT':
            lifestyle.append('Smoking cessation: counsel and consider pharmacotherapy.')
        if history.alcohol_consumption in ['MODERATE', 'HEAVY']:
            lifestyle.append('Alcohol reduction: limit to ≤1 drink/day for women, ≤2 for men.')
        if history.physical_activity in ['SEDENTARY', 'LIGHT']:
            lifestyle.append('Physical activity: aim for at least 150 minutes of moderate-intensity aerobic activity per week.')
        if history.diet_description:
            lifestyle.append('Dietary improvement: DASH diet rich in fruits, vegetables, whole grains, low-fat dairy, and reduced sodium.')
        else:
            lifestyle.append('Dietary recommendations: consider DASH diet, limit sodium to <2,300 mg/day (ideal <1,500 mg).')
        if history.family_history_hypertension:
            lifestyle.append('Family history of hypertension: emphasize lifestyle measures and regular monitoring.')
    except:
        # If no medical history, generic advice
        lifestyle.append('Smoking cessation, reduced alcohol intake, regular exercise, and DASH diet are recommended.')
        lifestyle.append('Limit sodium intake to <2,300 mg/day.')

    return lifestyle

def get_clinical_summary(patient, stage, recommendations, labs, lifestyle):
    """Generate a human-readable summary."""
    summary = f"Patient {patient.first_name} {patient.last_name} (ID: {patient.id}) - BP Assessment\n"
    summary += f"Stage: {stage or 'Undetermined'}\n"
    summary += f"Recommendations:\n"
    for rec in recommendations:
        summary += f"  - {rec['recommendation']} (Priority: {rec['priority']})\n"
    summary += f"\nSuggested Investigations:\n"
    for lab in labs:
        summary += f"  - {lab}\n"
    summary += f"\nLifestyle Modifications:\n"
    for item in lifestyle:
        summary += f"  - {item}\n"
    return summary

def get_cds_recommendations(patient):
    """
    Main entry point: returns structured CDS data for a patient.
    """
    # Get recent average BP
    avg_sys, avg_dia = get_recent_avg_bp(patient, days=30)
    latest = get_latest_reading(patient)
    stage = evaluate_hypertension_stage(avg_sys, avg_dia)

    # If no readings, stage = None
    if stage is None:
        return {
            'error': 'No recent BP readings available for this patient.',
            'stage': None,
            'recommendations': [],
            'labs': [],
            'lifestyle': [],
            'summary': 'Insufficient data.'
        }

    # Gather comorbidities from medical history
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
    except:
        pass

    # Get recommendations
    med_recs = get_medication_recommendations(patient, stage, comorbidities)
    labs = get_lab_recommendations(patient, stage, comorbidities)
    lifestyle = get_lifestyle_recommendations(patient, comorbidities)
    summary = get_clinical_summary(patient, stage, med_recs, labs, lifestyle)

    # Also include current medications (if any)
    current_meds = []
    try:
        history = patient.medical_history
        for med in history.current_medications.all():
            current_meds.append(med.name)
    except:
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
        'recommendations': med_recs,
        'labs': labs,
        'lifestyle': lifestyle,
        'summary': summary,
    }