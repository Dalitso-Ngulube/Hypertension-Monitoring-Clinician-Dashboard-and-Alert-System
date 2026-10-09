"""Non-validated demonstration risk scoring; not for clinical use."""

import math

from patients.models import PatientMedicalHistory


class WHORiskScore:
    """
    WHO/ISH 10-year cardiovascular risk prediction.
    Based on the WHO/ISH risk prediction charts (2007/2019).
    Uses: age, sex, systolic BP, BMI, smoking status, diabetes.
    For African region, we use the non-laboratory based version (uses BMI instead of cholesterol)
    for broader accessibility in primary care settings.
    """
    
    @staticmethod
    def calculate(patient, history):
        """Calculate 10-year cardiovascular risk using WHO/ISH algorithm."""
        age = patient.age
        gender = patient.gender
        
        bmi = None
        bmi_source = None

        if history and history.bmi is not None:
            bmi = float(history.bmi)
            bmi_source = 'history'

        if bmi is None and patient.height and patient.weight:
            height_m = float(patient.height)
            weight_kg = float(patient.weight)
            if height_m > 0 and weight_kg > 0:
                bmi = weight_kg / (height_m ** 2)
                bmi = round(bmi, 1)
                bmi_source = 'computed'

        if bmi is None:
            bmi = 24.0
            bmi_source = 'default'

        if bmi < 18.5:
            bmi_category = 'Underweight'
            bmi_coef = 0.0
        elif bmi < 25:
            bmi_category = 'Normal'
            bmi_coef = 0.0
        elif bmi < 30:
            bmi_category = 'Overweight'
            bmi_coef = 0.3
        else:
            bmi_category = 'Obese'
            bmi_coef = 0.6

        bmi_info = {
            'value': bmi,
            'category': bmi_category,
            'source': bmi_source,
        }

        # Get latest BP
        latest_reading = patient.bp_readings.order_by('-recorded_at').first()
        if not latest_reading:
            return None, None, 'info', bmi_info

        sys_bp = latest_reading.systolic

        # Risk factors
        smoker = history.smoking_status == 'CURRENT' if history else False
        diabetic = history.has_diabetes if history else False

        # ============================================================
        # WHO risk coefficients
        # ============================================================

        if gender == 'M':
            baseline_survival = 0.9500
            if age < 40:
                age_coef = 0.0000
            elif age < 50:
                age_coef = 0.2500
            elif age < 60:
                age_coef = 0.5000
            elif age < 70:
                age_coef = 0.8000
            else:
                age_coef = 1.1000

            if sys_bp < 120:
                bp_coef = 0.0000
            elif sys_bp < 140:
                bp_coef = 0.2000
            elif sys_bp < 160:
                bp_coef = 0.4500
            elif sys_bp < 180:
                bp_coef = 0.7000
            else:
                bp_coef = 1.0000

            smoker_coef = 0.6000 if smoker else 0
            diabetic_coef = 0.5000 if diabetic else 0

        else:
            baseline_survival = 0.9700

            if age < 40:
                age_coef = 0.0000
            elif age < 50:
                age_coef = 0.3000
            elif age < 60:
                age_coef = 0.6000
            elif age < 70:
                age_coef = 0.9000
            else:
                age_coef = 1.3000

            if sys_bp < 120:
                bp_coef = 0.0000
            elif sys_bp < 140:
                bp_coef = 0.2500
            elif sys_bp < 160:
                bp_coef = 0.5500
            elif sys_bp < 180:
                bp_coef = 0.8500
            else:
                bp_coef = 1.2000

            smoker_coef = 0.8000 if smoker else 0
            diabetic_coef = 0.7000 if diabetic else 0

        # ============================================================
        # Calculate total score (including BMI)
        # ============================================================
        score = age_coef + bp_coef + smoker_coef + diabetic_coef + bmi_coef

        # Calculate 10-year risk
        risk = 1 - baseline_survival ** math.exp(score)
        risk_percentage = round(risk * 100, 1)


        if risk_percentage < 5:
            category = 'Low'
            color = 'success'
        elif risk_percentage < 10:
            category = 'Low-Moderate'
            color = 'info'
        elif risk_percentage < 20:
            category = 'Moderate'
            color = 'warning'
        elif risk_percentage < 30:
            category = 'High'
            color = 'danger'
        else:
            category = 'Very High'
            color = 'danger'

        return risk_percentage, category, color, bmi_info


def get_risk_profile(patient):
    """
    Main entry point: returns comprehensive WHO/ISH risk profile for a patient.
    """
    try:
        history = patient.medical_history
    except PatientMedicalHistory.DoesNotExist:
        history = None
    
    risk_percentage, risk_category, risk_color, bmi_info = WHORiskScore.calculate(patient, history)
    is_complete = risk_percentage is not None and bmi_info['source'] != 'default'
    
    additional_risks = []
    if history:
        if history.has_kidney_disease: 
            additional_risks.append('Chronic Kidney Disease')
        if history.has_heart_disease: 
            additional_risks.append('Existing Heart Disease')
        if history.has_stroke_history: 
            additional_risks.append('Previous Stroke')
        if history.family_history_hypertension: 
            additional_risks.append('Family History of Hypertension')
        if history.family_history_diabetes: 
            additional_risks.append('Family History of Diabetes')
        if history.family_history_heart_disease: 
            additional_risks.append('Family History of Heart Disease')
        if history.smoking_status == 'CURRENT': 
            additional_risks.append('Current Smoker')
        elif history.smoking_status == 'FORMER': 
            additional_risks.append('Former Smoker')
        if history.alcohol_consumption in ['MODERATE', 'HEAVY']:
            additional_risks.append('Excessive Alcohol Consumption')
        if history.physical_activity in ['SEDENTARY', 'LIGHT']:
            additional_risks.append('Sedentary Lifestyle')
    
    if bmi_info['category'] in ['Overweight', 'Obese']:
        additional_risks.append(f'BMI: {bmi_info["value"]} ({bmi_info["category"]})')
    
    modifiable = []
    if history:
        if history.smoking_status == 'CURRENT': 
            modifiable.append('Smoking Cessation')
        if history.alcohol_consumption in ['MODERATE', 'HEAVY']: 
            modifiable.append('Reduce Alcohol Intake')
        if history.physical_activity in ['SEDENTARY', 'LIGHT']: 
            modifiable.append('Increase Physical Activity')
        if history.diet_description:
            # Add dietary improvement as a modifiable factor
            modifiable.append('Improve Dietary Habits')

    if bmi_info['category'] in ['Overweight', 'Obese']:
        modifiable.append('Weight Management (target BMI <25)')

    recommendations = get_risk_recommendations(risk_category, additional_risks, modifiable, bmi_info)

    return {
        'risk_percentage': risk_percentage,
        'risk_category': risk_category,
        'risk_color': risk_color,          # Now 'success', 'info', 'warning', 'danger'
        'bmi': bmi_info,
        'is_complete': is_complete,
        'additional_risk_factors': additional_risks,
        'modifiable_risk_factors': modifiable,
        'recommendations': recommendations,
    }


def get_risk_recommendations(category, additional_risks, modifiable, bmi_info):
    """Return non-prescriptive monitoring guidance for a demo risk category."""
    recommendations = [
        'Monitor blood pressure regularly and record readings.',
        'Discuss new or concerning symptoms with a qualified clinician.',
        'Continue lifestyle changes appropriate to individual circumstances.',
    ]
    return recommendations
