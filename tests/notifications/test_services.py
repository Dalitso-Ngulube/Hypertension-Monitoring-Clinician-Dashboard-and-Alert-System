from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from notifications.services import Notifier


class TestNotifier(TestCase):
    @patch('notifications.services.send_mail')
    def test_send_email(self, mock_send_mail):
        Notifier.send_email('test@example.com', 'Subject', 'Message')
        mock_send_mail.assert_called_once_with(
            'Subject', 
            'Message', 
            settings.DEFAULT_FROM_EMAIL, 
            ['test@example.com'],

        )

    @patch('notifications.services.send_mail', side_effect=Exception('SMTP error'))
    @patch('logging.Logger.error')
    def test_send_email_failure(self, mock_log, mock_send_mail):
        Notifier.send_email('test@example.com', 'Subject', 'Message')
        mock_log.assert_called_once()

    @patch('notifications.services.Client')
    def test_send_sms(self, mock_twilio_client):
        Notifier.send_sms('+123456789', 'Hello')
        mock_twilio_client.assert_called_once()

    def test_send_sms_no_phone(self):
        with patch('logging.Logger.info') as mock_log:
            Notifier.send_sms('', 'Hello')
            mock_log.assert_not_called()

    @patch('notifications.services.Client')
    def test_send_sms_twilio_call(self, mock_twilio_client):
        Notifier.send_sms('+123456789', 'Hello')
        mock_twilio_client.assert_called_once()
        mock_twilio_client.return_value.messages.create.assert_called_once_with(
            body='Hello',
            from_=settings.TWILIO_PHONE_NUMBER,
            to='+123456789'
        )
