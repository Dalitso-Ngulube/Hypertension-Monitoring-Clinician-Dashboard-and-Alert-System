import pytest
from django.core.exceptions import ValidationError
from alerts.models import Alert
from alerts.services import AlertEngine
from tests.factories import BPReadingFactory, PatientFactory

pytestmark = pytest.mark.django_db

class TestBPReadingModel:
    def test_risk_category_is_set_on_save(self):
        # AHA/ACC: 135/85 → STAGE_1 (systolic 130-139 or diastolic 80-89)
        reading = BPReadingFactory(systolic=135, diastolic=85)
        assert reading.risk_category == "STAGE_1"

        # 190/110 → CRISIS (systolic > 180)
        reading2 = BPReadingFactory(systolic=190, diastolic=110)
        assert reading2.risk_category == "CRISIS"

    def test_systolic_diastolic_validation(self):
        reading = BPReadingFactory.build(systolic=120, diastolic=150)
        with pytest.raises(ValidationError):
            reading.full_clean()

    def test_str(self):
        patient = PatientFactory(first_name="Jane")
        reading = BPReadingFactory(patient=patient, systolic=120, diastolic=80)
        assert str(reading) == f"{patient} - 120/80"

    def test_crisis_alerts_are_keyed_to_individual_readings(self):
        patient = PatientFactory()
        first_reading = BPReadingFactory(patient=patient, systolic=190, diastolic=110)
        second_reading = BPReadingFactory(patient=patient, systolic=200, diastolic=115)

        AlertEngine.check_crisis(first_reading)
        AlertEngine.check_crisis(second_reading)

        alerts = Alert.objects.filter(patient=patient, alert_type='CRISIS')
        assert alerts.count() == 2
        assert set(alerts.values_list('reading_id', flat=True)) == {
            first_reading.id,
            second_reading.id,
        }
