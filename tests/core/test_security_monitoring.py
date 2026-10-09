from unittest.mock import patch

import pytest
from django.test import RequestFactory, override_settings

from core.security.monitoring import SecurityMonitor
from tests.factories import UserFactory


@pytest.mark.django_db
@override_settings(ADMIN_EMAILS=['security@example.com'], DEFAULT_FROM_EMAIL='alerts@example.com')
@patch('core.security.monitoring.send_mail')
def test_suspicious_activity_adds_forwarded_ip_and_sends_admin_email(send_mail):
    request = RequestFactory().get(
        '/',
        HTTP_X_FORWARDED_FOR='203.0.113.4, 10.0.0.1',
        HTTP_USER_AGENT='Unit Test Browser',
    )
    details = {'reason': 'invalid token'}

    SecurityMonitor.log_suspicious(
        UserFactory(), 'invalid-login', details=details, request=request
    )

    assert details['ip'] == '203.0.113.4'
    assert details['user_agent'] == 'Unit Test Browser'
    send_mail.assert_called_once()
    assert send_mail.call_args.args[2:] == (
        'alerts@example.com', ['security@example.com']
    )


@override_settings(ADMIN_EMAILS=[])
@patch('core.security.monitoring.send_mail')
def test_suspicious_activity_uses_remote_address_and_skips_empty_admin_list(send_mail):
    request = RequestFactory().get('/', REMOTE_ADDR='192.0.2.8')
    details = {}

    SecurityMonitor.log_suspicious(None, 'blocked-request', details, request)

    assert details['ip'] == '192.0.2.8'
    assert details['user_agent'] == ''
    send_mail.assert_not_called()


@override_settings(ADMIN_EMAILS=['security@example.com'])
@patch('core.security.monitoring.logger.error')
@patch('core.security.monitoring.send_mail', side_effect=RuntimeError('SMTP down'))
def test_suspicious_activity_email_error_is_logged(send_mail, log_error):
    SecurityMonitor.log_suspicious(None, 'blocked-request')
    send_mail.assert_called_once()
    log_error.assert_called_once()


@patch('core.security.monitoring.logger.info')
@patch('core.security.monitoring.logger.warning')
def test_login_attempts_log_success_and_failure(log_warning, log_info):
    SecurityMonitor.log_login_attempt('alex', True, '192.0.2.1', 'agent')
    SecurityMonitor.log_login_attempt('alex', False)

    assert log_info.call_count == 1
    assert log_warning.call_count == 1


@patch('core.security.monitoring.logger.info')
def test_api_and_data_access_are_logged(log_info):
    request = RequestFactory().get('/', HTTP_X_FORWARDED_FOR='203.0.113.5')
    SecurityMonitor.log_api_access(None, 'GET', '/private', 200, request)
    SecurityMonitor.log_api_access(None, 'POST', '/private', 403)
    SecurityMonitor.log_data_access(None, 'patient', 12, action='export')

    assert log_info.call_count == 3