import pytest
from django.core.exceptions import ValidationError
from bp_readings.models import BPReading
from tests.factories import BPReadingFactory, PatientFactory

pytestmark = pytest.mark.django_db

class TestBPReadingModel:
    def test_risk_category_is_set_on_save(self):
        reading = BPReadingFactory(systolic=185, diastolic=100)
        assert reading.risk_category == "CRISIS"

        reading2 = BPReadingFactory(systolic=145, diastolic=92)
        assert reading2.risk_category == "STAGE_2"

    def test_systolic_diastolic_validation(self):
        # Use build to create an unsaved instance
        reading = BPReadingFactory.build(systolic=120, diastolic=150)  # invalid: diastolic > systolic
        with pytest.raises(ValidationError):
            reading.full_clean()   # this should raise ValidationError
            # reading.save() is not needed because full_clean already raises

    def test_str(self):
        patient = PatientFactory(first_name="Jane")
        reading = BPReadingFactory(patient=patient, systolic=120, diastolic=80)
        assert str(reading) == f"{patient} - 120/80"