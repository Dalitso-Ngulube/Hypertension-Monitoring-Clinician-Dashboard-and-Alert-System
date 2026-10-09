from unittest.mock import patch

import pytest

from alerts.models import Alert
from tests.factories import ClinicianFactory, PatientFactory, UserFactory

pytestmark = pytest.mark.django_db


@patch('notifications.dispatcher.Notifier.send_sms')
@patch('notifications.dispatcher.send_mail')
def test_critical_alert_notifies_clinician_and_patient(
    send_email, send_sms
):
    clinician = ClinicianFactory(email='clinician@example.com')
    patient_user = UserFactory(email='patient@example.com')
    patient = PatientFactory(
        clinician=clinician,
        user=patient_user,
        phone_number='+15555550123',
    )

    alert = Alert.objects.create(
        patient=patient,
        alert_type='CRISIS',
        severity='CRITICAL',
        message='Critical BP reading',
    )

    assert send_email.call_count == 2
    assert send_email.call_args_list[0].args[3] == ['clinician@example.com']
    assert send_email.call_args_list[1].args[3] == ['patient@example.com']
    assert send_sms.call_count == 1
    assert send_sms.call_args.args[0] == patient.phone_number
    assert send_email.call_args_list[0].args[1] == alert.message


@patch('notifications.dispatcher.Notifier.send_sms', side_effect=RuntimeError('sms down'))
@patch('notifications.dispatcher.send_mail', side_effect=RuntimeError('email down'))
def test_notification_failures_do_not_abort_alert_creation(
    send_email, send_sms
):
    clinician = ClinicianFactory(email='clinician@example.com')
    patient = PatientFactory(clinician=clinician, phone_number='+15555550123')

    alert = Alert.objects.create(
        patient=patient,
        alert_type='CRISIS',
        severity='HIGH',
        message='High BP reading',
    )

    assert alert.pk is not None
    assert send_email.called
    send_sms.assert_called_once()


def test_low_severity_alert_does_not_send_notifications():
    patient = PatientFactory(phone_number='+15555550123')

    with patch('notifications.dispatcher.Notifier.send_sms') as send_sms:
        with patch('notifications.dispatcher.send_mail') as send_email:
            Alert.objects.create(
                patient=patient,
                alert_type='INFO',
                severity='LOW',
                message='Informational alert',
            )

    send_sms.assert_not_called()
    send_email.assert_not_called()


@patch('notifications.dispatcher.Notifier.send_sms')
@patch('notifications.dispatcher.send_mail')
def test_alert_update_does_not_resend_notifications(send_email, send_sms):
    alert = Alert.objects.create(
        patient=PatientFactory(),
        alert_type='CRISIS',
        severity='CRITICAL',
        message='Critical BP reading',
    )
    send_email.reset_mock()
    send_sms.reset_mock()

    alert.is_resolved = True
    alert.save()

    send_email.assert_not_called()
    send_sms.assert_not_called()