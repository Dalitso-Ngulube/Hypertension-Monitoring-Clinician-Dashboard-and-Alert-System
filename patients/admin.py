from django.contrib import admin
from .models import (
    Patient, MedicalCondition, Allergy, Medication, PatientMedicalHistory
)


@admin.register(MedicalCondition)
class MedicalConditionAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name', 'description']


@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    list_display = ['name', 'severity']
    list_filter = ['severity']
    search_fields = ['name', 'common_symptoms']


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'generic_name', 'category']
    list_filter = ['category']
    search_fields = ['name', 'generic_name', 'description']


class PatientMedicalHistoryInline(admin.StackedInline):
    model = PatientMedicalHistory
    can_delete = False
    verbose_name_plural = 'Medical History'
    filter_horizontal = ['conditions', 'allergies', 'current_medications']
    fieldsets = (
        ('Medical Conditions', {
            'fields': ('conditions', 'condition_notes')
        }),
        ('Allergies', {
            'fields': ('allergies', 'allergy_notes')
        }),
        ('Current Medications', {
            'fields': ('current_medications', 'current_medication_notes')
        }),
        ('Comorbidities', {
            'fields': ('has_diabetes', 'has_kidney_disease', 'has_heart_disease',
                       'has_stroke_history', 'comorbidity_notes')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_name', 'emergency_phone', 'emergency_relationship')
        }),
        ('Lifestyle', {
            'fields': ('smoking_status', 'smoking_pack_years', 'alcohol_consumption',
                       'physical_activity', 'diet_description')
        }),
        ('Family History', {
            'fields': ('family_history_hypertension', 'family_history_diabetes',
                       'family_history_heart_disease', 'family_history_stroke',
                       'family_history_notes')
        }),
    )


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'first_name', 'last_name', 'age', 'gender', 'clinician']
    exclude = ('user',)                    # Hide user field from the edit form
    list_filter = ['gender', 'clinician']
    search_fields = ['first_name', 'last_name', 'phone_number']
    inlines = [PatientMedicalHistoryInline]

    def save_model(self, request, obj, form, change):
        # Auto-assign the logged-in user when creating a new patient
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def get_inline_instances(self, request, obj=None):
        # Ensure each patient has a medical history record
        if obj:
            PatientMedicalHistory.objects.get_or_create(patient=obj)
        return super().get_inline_instances(request, obj)