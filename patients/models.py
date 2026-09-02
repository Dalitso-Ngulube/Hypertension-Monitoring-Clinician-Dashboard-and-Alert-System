from django.conf import settings
from django.db import models


class Patient(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='patient'
    )
    clinician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patients'
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField(default=0)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    id = models.AutoField(primary_key=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Height in meters (e.g., 1.75)")
    weight = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, help_text="Weight in kilograms (e.g., 72.5)")

    @property
    def bmi(self):
        if self.height and self.weight:
            return round(self.weight / (self.height ** 2), 1)
        return None

    def __str__(self):
        return f"{self.first_name} {self.last_name}" or f"Patient {self.id}"

    class Meta:
        ordering = ['-created_at']


class MedicalCondition(models.Model):
    """Pre-defined medical conditions for selection"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=(
        ('CARDIOVASCULAR', 'Cardiovascular'),
        ('RESPIRATORY', 'Respiratory'),
        ('ENDOCRINE', 'Endocrine'),
        ('GASTROINTESTINAL', 'Gastrointestinal'),
        ('NEUROLOGICAL', 'Neurological'),
        ('RENAL', 'Renal'),
        ('AUTOIMMUNE', 'Autoimmune'),
        ('INFECTIOUS', 'Infectious'),
        ('MENTAL', 'Mental Health'),
        ('OTHER', 'Other'),
    ), default='OTHER')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Allergy(models.Model):
    """Pre-defined allergies"""
    SEVERITY_CHOICES = (
        ('MILD', 'Mild'),
        ('MODERATE', 'Moderate'),
        ('SEVERE', 'Severe'),
        ('LIFE_THREATENING', 'Life Threatening'),
    )
    name = models.CharField(max_length=100, unique=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='MILD')
    common_symptoms = models.TextField(blank=True)
    treatment = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Allergies'


class Medication(models.Model):
    """Pre-defined medications"""
    CATEGORY_CHOICES = (
        ('ANTIHYPERTENSIVE', 'Antihypertensive'),
        ('DIURETIC', 'Diuretic'),
        ('BETA_BLOCKER', 'Beta Blocker'),
        ('CALCIUM_CHANNEL', 'Calcium Channel Blocker'),
        ('ACE_INHIBITOR', 'ACE Inhibitor'),
        ('ARB', 'ARB'),
        ('STATIN', 'Statin'),
        ('ANTICOAGULANT', 'Anticoagulant'),
        ('ANTIDIABETIC', 'Antidiabetic'),
        ('OTHER', 'Other'),
    )

    name = models.CharField(max_length=100)
    generic_name = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='OTHER')
    description = models.TextField(blank=True)
    side_effects = models.TextField(blank=True)
    contraindications = models.TextField(blank=True)
    dosage_forms = models.CharField(max_length=200, blank=True, help_text="e.g., Tablet, Capsule, Liquid")

    def __str__(self):
        return f"{self.name} ({self.category})"

    class Meta:
        ordering = ['name']


class PatientMedicalHistory(models.Model):
    """Patient's complete medical history"""
    patient = models.OneToOneField(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='medical_history'
    )

    # Medical History
    conditions = models.ManyToManyField(
        MedicalCondition,
        blank=True,
        related_name='patients_with_condition'
    )
    condition_notes = models.TextField(blank=True, help_text="Additional details about conditions")

    # Allergies
    allergies = models.ManyToManyField(
        Allergy,
        blank=True,
        related_name='patients_with_allergy'
    )
    allergy_notes = models.TextField(blank=True, help_text="Additional allergy details")

    # Medications
    current_medications = models.ManyToManyField(
        Medication,
        blank=True,
        related_name='patients_currently_on'
    )
    current_medication_notes = models.TextField(blank=True, help_text="Dosage, frequency, etc.")

    # Comorbidities
    has_diabetes = models.BooleanField(default=False)
    has_kidney_disease = models.BooleanField(default=False)
    has_heart_disease = models.BooleanField(default=False)
    has_stroke_history = models.BooleanField(default=False)
    comorbidity_notes = models.TextField(blank=True)

    # Emergency Contact
    emergency_name = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    emergency_relationship = models.CharField(max_length=50, blank=True)

    # Lifestyle
    smoking_status = models.CharField(max_length=20, choices=(
        ('NEVER', 'Never Smoked'),
        ('FORMER', 'Former Smoker'),
        ('CURRENT', 'Current Smoker'),
    ), default='NEVER')
    smoking_pack_years = models.PositiveIntegerField(null=True, blank=True, help_text="Pack-years if applicable")

    alcohol_consumption = models.CharField(max_length=20, choices=(
        ('NONE', 'None'),
        ('LIGHT', 'Light (1-2 drinks/week)'),
        ('MODERATE', 'Moderate (3-14 drinks/week)'),
        ('HEAVY', 'Heavy (>14 drinks/week)'),
    ), default='NONE')

    physical_activity = models.CharField(max_length=20, choices=(
        ('SEDENTARY', 'Sedentary'),
        ('LIGHT', 'Light (1-2 days/week)'),
        ('MODERATE', 'Moderate (3-5 days/week)'),
        ('ACTIVE', 'Active (6-7 days/week)'),
    ), default='SEDENTARY')

    diet_description = models.TextField(blank=True, help_text="Dietary habits and restrictions")

    # Family History
    family_history_hypertension = models.BooleanField(default=False)
    family_history_diabetes = models.BooleanField(default=False)
    family_history_heart_disease = models.BooleanField(default=False)
    family_history_stroke = models.BooleanField(default=False)
    family_history_notes = models.TextField(blank=True)

    bmi = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Body Mass Index (kg/m²). If not provided, it will be computed from height/weight."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Medical History for {self.patient}"

    class Meta:
        verbose_name_plural = 'Patient Medical Histories'