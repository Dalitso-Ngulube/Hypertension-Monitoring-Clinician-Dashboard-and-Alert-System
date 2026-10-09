import pytest
from unittest.mock import patch

from alerts.tasks import process_alert
from tests.factories import (
    AlertFactory,
    ClinicianFactory,
    PatientFactory,
    UserFactory,
)

pytestmark = pytest.mark.django_db


@patch('alerts.tasks.Notifier.send_email')
@patch('alerts.tasks.Notifier.send_sms')
def test_process_crisis_alert_sends_sms_and_patient_email(send_sms, send_email):
    user = UserFactory(email='patient@example.com')
    clinician = ClinicianFactory()
    patient = PatientFactory(
        user=user,
        clinician=clinician,
        phone_number='+15555550123',
    )
    alert = AlertFactory(patient=patient, alert_type='CRISIS')

    process_alert(alert.id)

    assert send_sms.call_count == 2
    assert send_sms.call_args_list[-1].args == (
        patient.phone_number, alert.message
    )
    assert send_email.call_count == 1
    assert send_email.call_args_list[-1].args == (
        'patient@example.com', f'Alert: {alert.alert_type}', alert.message
    )


@patch('alerts.tasks.Notifier.send_email')
@patch('alerts.tasks.Notifier.send_sms')
def test_process_non_crisis_without_email_skips_notifications(send_sms, send_email):
    user = UserFactory(email='')
    patient = PatientFactory(
        user=user,
        clinician=ClinicianFactory(email=''),
        phone_number='',
    )
    alert = AlertFactory(patient=patient, alert_type='WARNING', severity='LOW')

    process_alert(alert.id)

    send_sms.assert_not_called()
    send_email.assert_not_called()