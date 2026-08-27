from rest_framework import serializers
from .models import (
    Patient, MedicalCondition, Allergy, Medication,
    PatientMedicalHistory
)

class PatientSerializer(serializers.ModelSerializer):
    """Basic patient serializer (for list views)"""
    class Meta:
        model = Patient
        fields = [
            'id', 'first_name', 'last_name', 'age', 'gender',
            'phone_number', 'address', 'created_at', 'updated_at',
            'user', 'clinician'
        ]
        read_only_fields = ('user', 'created_at', 'updated_at')


# Medical History Serializers

class MedicalConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalCondition
        fields = ['id', 'name', 'description', 'category']


class AllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergy
        fields = ['id', 'name', 'severity', 'common_symptoms', 'treatment']


class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = ['id', 'name', 'generic_name', 'category', 'description', 'side_effects', 'contraindications']


class PatientMedicalHistorySerializer(serializers.ModelSerializer):
    # Nested serializers for related data
    conditions = MedicalConditionSerializer(many=True, read_only=True)
    allergies = AllergySerializer(many=True, read_only=True)
    current_medications = MedicationSerializer(many=True, read_only=True)

    # For writing (using IDs)
    condition_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    allergy_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    medication_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = PatientMedicalHistory
        fields = [
            'id',
            'patient',
            'conditions',
            'condition_ids',
            'condition_notes',
            'allergies',
            'allergy_ids',
            'allergy_notes',
            'current_medications',
            'medication_ids',
            'current_medication_notes',
            'has_diabetes',
            'has_kidney_disease',
            'has_heart_disease',
            'has_stroke_history',
            'comorbidity_notes',
            'emergency_name',
            'emergency_phone',
            'emergency_relationship',
            'smoking_status',
            'smoking_pack_years',
            'alcohol_consumption',
            'physical_activity',
            'diet_description',
            'family_history_hypertension',
            'family_history_diabetes',
            'family_history_heart_disease',
            'family_history_stroke',
            'family_history_notes',
            'bmi',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['patient', 'created_at', 'updated_at']
        extra_kwargs = {
            'condition_notes': {'required': False},
            'allergy_notes': {'required': False},
            'current_medication_notes': {'required': False},
            'has_diabetes': {'required': False},
            'has_kidney_disease': {'required': False},
            'has_heart_disease': {'required': False},
            'has_stroke_history': {'required': False},
            'comorbidity_notes': {'required': False},
            'emergency_name': {'required': False},
            'emergency_phone': {'required': False},
            'emergency_relationship': {'required': False},
            'smoking_status': {'required': False},
            'smoking_pack_years': {'required': False},
            'alcohol_consumption': {'required': False},
            'physical_activity': {'required': False},
            'diet_description': {'required': False},
            'family_history_hypertension': {'required': False},
            'family_history_diabetes': {'required': False},
            'family_history_heart_disease': {'required': False},
            'family_history_stroke': {'required': False},
            'family_history_notes': {'required': False},
            'bmi': {'required': False},
        }

    def update(self, instance, validated_data):
        # Handle many-to-many relationships
        condition_ids = validated_data.pop('condition_ids', None)
        allergy_ids = validated_data.pop('allergy_ids', None)
        medication_ids = validated_data.pop('medication_ids', None)

        # Update regular fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update many-to-many fields
        if condition_ids is not None:
            instance.conditions.set(condition_ids)
        if allergy_ids is not None:
            instance.allergies.set(allergy_ids)
        if medication_ids is not None:
            instance.current_medications.set(medication_ids)

        instance.save()
        return instance


class PatientDetailSerializer(serializers.ModelSerializer):
    medical_history = PatientMedicalHistorySerializer(read_only=True)

    class Meta:
        model = Patient
        fields = [
            'id',
            'user',
            'clinician',
            'first_name',
            'last_name',
            'age',
            'gender',
            'phone_number',
            'address',
            'created_at',
            'updated_at',
            'medical_history',
        ]
        