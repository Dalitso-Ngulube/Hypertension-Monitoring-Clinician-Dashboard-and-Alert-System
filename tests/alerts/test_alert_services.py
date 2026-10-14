from unittest.mock import patch
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone

from alerts.models import Alert
from alerts.management.commands.check_missed_readings import Command
from alerts.services import AlertEngine
from tests.factories import BPReadingFactory, PatientFactory

pytestmark = pytest.mark.django_db


def test_crisis_reading_creates_one_alert():
    reading = BPReadingFactory(systolic=190, diastolic=125)

    assert AlertEngine.check_crisis(reading) is True
    assert Alert.objects.filter(reading=reading, alert_type='CRISIS').count() == 1
    assert AlertEngine.check_crisis(reading) is True
    assert Alert.objects.filter(reading=reading, alert_type='CRISIS').count() == 1


def test_non_crisis_reading_does_not_create_alert():
    reading = BPReadingFactory(systolic=130, diastolic=80)

    assert AlertEngine.check_crisis(reading) is False
    assert not Alert.objects.filter(reading=reading).exists()


def test_three_elevated_readings_create_trend_alert():
    patient = PatientFactory()
    for pressure in [145, 140, 135]:
        BPReadingFactory(patient=patient, systolic=pressure, diastolic=95)

    assert AlertEngine.check_trend(patient) is True
    assert Alert.objects.filter(patient=patient, alert_type='TRENDING_UP').exists()


def test_trend_alert_does_not_fire_twice_within_window():
    patient = PatientFactory()
    for pressure in [145, 140, 135]:
        BPReadingFactory(patient=patient, systolic=pressure, diastolic=95)

    AlertEngine.check_trend(patient)
    AlertEngine.check_trend(patient)

    assert Alert.objects.filter(
        patient=patient,
        alert_type='TRENDING_UP',
        is_resolved=False,
    ).count() == 1


def test_trend_alert_fires_again_after_window():
    patient = PatientFactory()
    for pressure in [145, 140, 135]:
        BPReadingFactory(patient=patient, systolic=pressure, diastolic=95)

    first_now = timezone.now()
    with patch('alerts.services.timezone.now', return_value=first_now):
        AlertEngine.check_trend(patient)

    with patch(
        'alerts.services.timezone.now',
        return_value=first_now + timedelta(days=8),
    ):
        AlertEngine.check_trend(patient)

    assert Alert.objects.filter(
        patient=patient, alert_type='TRENDING_UP'
    ).count() == 2


def test_trend_with_normal_reading_does_not_alert():
    patient = PatientFactory()
    for pressure in [115, 120, 135]:
        BPReadingFactory(patient=patient, systolic=pressure, diastolic=70)

    assert AlertEngine.check_trend(patient) is False
    assert not Alert.objects.filter(patient=patient, alert_type='TRENDING_UP').exists()


def test_missed_reading_alert_for_reading_older_than_48_hours():
    reading = BPReadingFactory()
    type(reading).objects.filter(pk=reading.pk).update(
        recorded_at=timezone.now() - timedelta(hours=49)
    )
    reading.refresh_from_db()

    assert AlertEngine.check_missed_readings(reading.patient) is True
    assert Alert.objects.filter(
        patient=reading.patient, alert_type='MISSED_READING'
    ).exists()


def test_recent_or_missing_reading_does_not_create_missed_alert():
    patient = PatientFactory()
    reading = BPReadingFactory(patient=patient)

    assert AlertEngine.check_missed_readings(patient) is False
    reading.delete()
    assert AlertEngine.check_missed_readings(patient) is False


def test_check_missed_readings_command_notifies_patients_without_recent_readings():
    from django.utils import timezone

    patient = PatientFactory()
    stale = BPReadingFactory(patient=patient)
    type(stale).objects.filter(pk=stale.pk).update(
        recorded_at=timezone.now() - timedelta(days=3)
    )

    from unittest.mock import patch

    with patch.object(AlertEngine, 'check_missed_readings') as check_missed:
        Command().handle()

    assert check_missed.call_count == 2
    assert patient in [call.args[0] for call in check_missed.call_args_list]


def test_missed_reading_alert_does_not_fire_twice_within_window():
    """A second missed-reading alert should be suppressed within 14 days."""
    patient = PatientFactory()
    reading = BPReadingFactory(patient=patient)
    type(reading).objects.filter(pk=reading.pk).update(
        recorded_at=timezone.now() - timedelta(days=5)
    )

    AlertEngine.check_missed_readings(patient)
    AlertEngine.check_missed_readings(patient)

    assert Alert.objects.filter(
        patient=patient,
        alert_type='MISSED_READING',
        is_resolved=False,
    ).count() == 1


def test_missed_reading_alert_fires_again_after_window():
    """A new missed-reading alert should fire once the 14-day window elapses."""
    patient = PatientFactory()
    reading = BPReadingFactory(patient=patient)
    type(reading).objects.filter(pk=reading.pk).update(
        recorded_at=timezone.now() - timedelta(days=5)
    )

    first_now = timezone.now()
    with patch('alerts.services.timezone.now', return_value=first_now):
        AlertEngine.check_missed_readings(patient)

    with patch(
        'alerts.services.timezone.now',
        return_value=first_now + timedelta(days=15),
    ):
        AlertEngine.check_missed_readings(patient)

    assert Alert.objects.filter(
        patient=patient, alert_type='MISSED_READING'
    ).count() == 2