import pytest

from alerts.models import Alert
from bp_readings.models import BPReading
from core.services import create_alert_for_reading, handle_bp_reading_created
from tests.factories import BPReadingFactory

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'systolic,diastolic,severity,message_part',
    [
        (190, 125, 'CRITICAL', 'Crisis'),
        (180, 100, 'CRITICAL', 'Critical'),
        (150, 95, 'HIGH', 'High'),
    ],
)
def test_create_alert_for_high_reading(
    systolic, diastolic, severity, message_part
):
    reading = BPReadingFactory(systolic=systolic, diastolic=diastolic)

    create_alert_for_reading(reading)

    alert = Alert.objects.filter(patient=reading.patient).order_by('-id').first()
    assert alert is not None
    assert alert.severity == severity
    assert message_part in alert.message


def test_create_alert_for_normal_reading_is_noop():
    reading = BPReadingFactory(systolic=115, diastolic=75)

    create_alert_for_reading(reading)

    assert not Alert.objects.filter(patient=reading.patient).exists()


def test_handle_reading_reclassifies_and_persists_alert():
    reading = BPReadingFactory(systolic=190, diastolic=125)
    BPReading.objects.filter(pk=reading.pk).update(risk_category='NORMAL')
    reading.refresh_from_db()

    handle_bp_reading_created(reading)

    reading.refresh_from_db()
    assert reading.risk_category == 'CRISIS'
    assert Alert.objects.filter(patient=reading.patient).exists()