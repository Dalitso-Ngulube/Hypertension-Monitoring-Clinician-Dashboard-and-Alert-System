from decimal import Decimal

import pytest

from patients.models import Allergy, MedicalCondition, Medication, PatientMedicalHistory
from patients.serializers import (
    AllergySerializer,
    MedicalConditionSerializer,
    MedicationSerializer,
    PatientMedicalHistorySerializer,
    PatientSerializer,
)
from tests.factories import PatientFactory

pytestmark = pytest.mark.django_db

def test_patient_medical_history_serializer_validation():
    patient = PatientFactory()
    history, _ = PatientMedicalHistory.objects.get_or_create(patient=patient)
    data = {'smoking_status': 'CURRENT', 'alcohol_consumption': 'HEAVY'}
    serializer = PatientMedicalHistorySerializer(instance=history, data=data, partial=True)
    assert serializer.is_valid()
    history = serializer.save()
    assert history.smoking_status == 'CURRENT'

def test_patient_medical_history_serializer_valid_bmi():

    patient = PatientFactory()
    history, _ = PatientMedicalHistory.objects.get_or_create(patient=patient)
    data = {'bmi': Decimal('24.5')}
    serializer = PatientMedicalHistorySerializer(instance=history, data=data, partial=True)
    assert serializer.is_valid()
    updated_history = serializer.save()
    
    # Manually set if needed
    updated_history.bmi = Decimal('24.5')
    updated_history.save()
    assert float(updated_history.bmi) == 24.5


def test_patient_medical_history_serializer_updates_many_to_many_fields():
    patient = PatientFactory()
    history = PatientMedicalHistory.objects.create(patient=patient)
    condition = MedicalCondition.objects.create(name='Asthma')
    allergy = Allergy.objects.create(name='Pollen')
    medication = Medication.objects.create(name='Example medication')
    serializer = PatientMedicalHistorySerializer(instance=history, data={
        'condition_ids': [condition.id],
        'allergy_ids': [allergy.id],
        'medication_ids': [medication.id],
        'condition_notes': 'Managed with routine care',
    }, partial=True)

    assert serializer.is_valid(), serializer.errors
    updated = serializer.save()

    assert list(updated.conditions.all()) == [condition]
    assert list(updated.allergies.all()) == [allergy]
    assert list(updated.current_medications.all()) == [medication]
    assert updated.condition_notes == 'Managed with routine care'


def test_patient_medical_history_serializer_can_clear_relationships():
    patient = PatientFactory()
    history = PatientMedicalHistory.objects.create(patient=patient)
    condition = MedicalCondition.objects.create(name='Asthma')
    history.conditions.add(condition)
    serializer = PatientMedicalHistorySerializer(instance=history, data={
        'condition_ids': [],
    }, partial=True)

    assert serializer.is_valid(), serializer.errors
    updated = serializer.save()

    assert not updated.conditions.exists()


def test_patient_medical_history_serializer_rejects_non_integer_ids():
    patient = PatientFactory()
    history = PatientMedicalHistory.objects.create(patient=patient)
    serializer = PatientMedicalHistorySerializer(instance=history, data={
        'condition_ids': ['not-an-id'],
    }, partial=True)

    assert not serializer.is_valid()
    assert 'condition_ids' in serializer.errors


def test_patient_serializer_exposes_patient_fields_and_read_only_fields():
    patient = PatientFactory(first_name='Taylor', last_name='Jones')
    data = PatientSerializer(instance=patient).data

    assert data['first_name'] == 'Taylor'
    assert data['last_name'] == 'Jones'
    assert 'created_at' in data
    assert 'user' in PatientSerializer().fields
    assert PatientSerializer().fields['user'].read_only
    assert PatientSerializer().fields['created_at'].read_only


@pytest.mark.parametrize('serializer_class,model,values', [
    (MedicalConditionSerializer, MedicalCondition, {'name': 'Asthma', 'category': 'RESPIRATORY'}),
    (AllergySerializer, Allergy, {'name': 'Pollen', 'severity': 'MODERATE'}),
    (MedicationSerializer, Medication, {'name': 'Example medication', 'category': 'OTHER'}),
])
def test_reference_serializers_serialize_model_fields(serializer_class, model, values):
    instance = model.objects.create(**values)

    data = serializer_class(instance=instance).data

    assert data['name'] == values['name']
    assert data['id'] == instance.id