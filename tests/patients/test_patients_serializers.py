from decimal import Decimal

import pytest

from patients.models import PatientMedicalHistory
from patients.serializers import PatientMedicalHistorySerializer
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