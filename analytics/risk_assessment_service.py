import math
from patients.models import Patient, PatientMedicalHistory
from bp_readings.models import BPReading

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
        
        # Get latest BP
        latest_reading = patient.bp_readings.order_by('-recorded_at').first()
        if not latest_reading:
            return None, None, 'Insufficient Data'
        
        sys_bp = latest_reading.systolic
        
        # Risk factors
        smoker = history.smoking_status == 'CURRENT' if history else False
        diabetic = (history.has_diabetes or history.has_diabetes_treatment) if history else False
    
        bmi = None
        bmi_source = None
        
        # Check if BMI is stored directly in medical history
        if history and history.bmi is not None:
            bmi = float(history.bmi)
            bmi_source = 'history'
        
        # If not, compute from height and weight (if available on patient)
        if bmi is None and patient.height and patient.weight:
            height_m = float(patient.height)
            weight_kg = float(patient.weight)
            if height_m > 0 and weight_kg > 0:
                bmi = weight_kg / (height_m ** 2)
                bmi = round(bmi, 1)
                bmi_source = 'computed'
        
        # If BMI is still None, use a reasonable default (24.0 = normal)
        if bmi is None:
            bmi = 24.0
            bmi_source = 'default'
        
        # BMI categories (WHO classification)
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
        
        # ============================================================
        # WHO risk coefficients (African region, non-laboratory based)
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
        
        # WHO categories
        if risk_percentage < 5:
            category = 'Low'
            color = 'bg-emerald-100 text-emerald-700 border-emerald-300'
        elif risk_percentage < 10:
            category = 'Low-Moderate'
            color = 'bg-green-100 text-green-700 border-green-300'
        elif risk_percentage < 20:
            category = 'Moderate'
            color = 'bg-amber-100 text-amber-700 border-amber-300'
        elif risk_percentage < 30:
            category = 'High'
            color = 'bg-orange-100 text-orange-700 border-orange-300'
        else:
            category = 'Very High'
            color = 'bg-rose-100 text-rose-700 border-rose-300'
        
        bmi_info = {
            'value': bmi,
            'category': bmi_category,
            'source': bmi_source,
        }
        
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
            modifiable.append('Improve Diet (DASH)')
    
    if bmi_info['category'] in ['Overweight', 'Obese']:
        modifiable.append('Weight Management (target BMI <25)')
    
    recommendations = get_risk_recommendations(risk_category, additional_risks, modifiable, bmi_info)
    
    return {
        'risk_percentage': risk_percentage,
        'risk_category': risk_category,
        'risk_color': risk_color,
        'bmi': bmi_info,
        'is_complete': is_complete,
        'additional_risk_factors': additional_risks,
        'modifiable_risk_factors': modifiable,
        'recommendations': recommendations,
    }


def get_risk_recommendations(category, additional_risks, modifiable, bmi_info):
    """Generate evidence-based recommendations based on WHO/ISH guidelines."""
    recs = []
    
    if category == 'Very High':
        recs.append('[URGENT] Immediate specialist referral recommended.')
        recs.append('[MEDICATION] Initiate statin therapy (high-intensity).')
        recs.append('[MEDICATION] Initiate or optimize antihypertensive therapy to achieve BP <140/90 (or <130/80 if diabetic/CKD).')
        recs.append('[MEDICATION] Consider aspirin therapy (if no contraindications).')
        recs.append('[MONITOR] Monitor BP and lipids every 3 months.')
        
    elif category == 'High':
        recs.append('[MEDICATION] Initiate statin therapy (moderate-intensity).')
        recs.append('[MEDICATION] Optimize antihypertensive therapy.')
        recs.append('[MONITOR] Monitor BP every 3-6 months.')
        recs.append('[FOLLOW-UP] Reassess risk in 6-12 months.')
        
    elif category == 'Moderate':
        recs.append('[MEDICATION] Consider statin therapy (low-to-moderate intensity).')
        recs.append('[MONITOR] Monitor BP regularly.')
        recs.append('[FOLLOW-UP] Reassess risk in 1 year.')
        recs.append('[LIFESTYLE] Continue lifestyle modifications.')
        
    elif category == 'Low-Moderate':
        recs.append('[LIFESTYLE] Lifestyle modifications recommended.')
        recs.append('[MONITOR] Monitor BP annually.')
        recs.append('[FOLLOW-UP] Reassess risk in 2 years.')
        
    else:  # Low
        recs.append('[LIFESTYLE] Continue healthy lifestyle measures.')
        recs.append('[FOLLOW-UP] Reassess in 2-3 years.')
    
    # BMI-specific recommendations
    if bmi_info and bmi_info['category'] == 'Obese':
        recs.append('[WEIGHT] Weight loss: aim for 5-10% weight loss over 6 months.')
        recs.append('[REFERRAL] Consider referral to dietitian for nutritional counseling.')
    elif bmi_info and bmi_info['category'] == 'Overweight':
        recs.append('[WEIGHT] Weight management: aim for 5% weight loss over 6 months.')
        recs.append('[DIET] Review dietary habits and physical activity.')
    
    # Additional recommendations based on specific risk factors
    if 'Current Smoker' in additional_risks:
        recs.append('[SMOKING] Strongly advise smoking cessation. Consider nicotine replacement therapy.')
    if 'Chronic Kidney Disease' in additional_risks:
        recs.append('[RENAL] Monitor renal function and consider ACE inhibitor or ARB.')
    if 'Family History of Heart Disease' in additional_risks:
        recs.append('[FAMILY] Family history indicates higher risk – emphasize lifestyle measures.')
    if 'Excessive Alcohol Consumption' in additional_risks:
        recs.append('[ALCOHOL] Reduce alcohol intake to <=1 drink/day (women) or <=2 drinks/day (men).')
    if 'Sedentary Lifestyle' in additional_risks:
        recs.append('[EXERCISE] Aim for at least 150 minutes of moderate-intensity exercise per week.')
    
    # Add modifiable factors
    for item in modifiable:
        recs.append(f'[MODIFY] {item}')
    
    # Remove duplicates while preserving order
    seen = set()
    unique_recs = []
    for rec in recs:
        if rec not in seen:
            seen.add(rec)
            unique_recs.append(rec)
    
    return unique_recs
