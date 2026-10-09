from unittest.mock import patch

import pytest

from alerts.models import Alert
from notifications.dispatcher import NotificationDispatcher
from notifications.models import NotificationLog
from tests.factories import PatientFactory

pytestmark = pytest.mark.django_db


@patch('notifications.dispatcher.Notifier.send_sms')
@patch('notifications.dispatcher.send_mail')
def test_critical_alert_dispatches_notification_email_and_sms(
    send_mail, send_sms
):
    patient = PatientFactory(phone_number='+15555550123')
    alert = Alert.objects.create(
        patient=patient,
        alert_type='CRISIS',
        severity='CRITICAL',
        message='Critical reading',
    )
    send_mail.reset_mock()
    send_sms.reset_mock()

    NotificationDispatcher.dispatch(alert)

    assert NotificationLog.objects.filter(
        recipient=patient.user,
        channel='email',
        message=alert.message,
        status='sent',
    ).exists()
    assert send_mail.call_count == 2
    send_sms.assert_called_once()
    assert send_sms.call_args.args[0] == patient.phone_number
    assert patient.first_name in send_sms.call_args.args[1]


@patch('notifications.dispatcher.Notifier.send_sms')
@patch('notifications.dispatcher.send_mail')
def test_high_alert_creates_delivery_log_and_sends_notification(send_mail, send_sms):
    patient = PatientFactory(phone_number='+15555550123')
    alert = Alert.objects.create(
        patient=patient,
        alert_type='WARNING',
        severity='HIGH',
        message='High reading',
    )
    send_mail.reset_mock()
    send_sms.reset_mock()

    NotificationDispatcher.dispatch(alert)

    assert NotificationLog.objects.filter(
        recipient=patient.user,
        channel='email',
        message=alert.message,
        status='sent',
    ).exists()
    assert send_mail.called
    assert send_sms.called


@patch('notifications.dispatcher.send_mail')
def test_critical_alert_without_phone_skips_sms(send_mail):
    patient = PatientFactory(phone_number='')
    alert = Alert.objects.create(
        patient=patient,
        alert_type='CRISIS',
        severity='CRITICAL',
        message='Critical reading',
    )
    send_mail.reset_mock()

    with patch('notifications.dispatcher.Notifier.send_sms') as send_sms:
        NotificationDispatcher.dispatch(alert)

    assert send_mail.called
    send_sms.assert_not_called()


@patch('notifications.dispatcher.send_mail')
def test_notificationlog_written_on_dispatch(send_mail):
    patient = PatientFactory(phone_number='')
    alert = Alert.objects.create(
        patient=patient,
        alert_type='CRISIS',
        severity='CRITICAL',
        message='Dispatch audit test',
    )
    send_mail.reset_mock()

    NotificationDispatcher.dispatch(alert)

    log = NotificationLog.objects.filter(
        recipient=patient.user,
        channel='email',
        message='Dispatch audit test',
    ).latest('id')
    assert log.subject.startswith('ALERT: CRITICAL')
    assert log.status == 'sent'
    assert send_mail.call_count >= 1
