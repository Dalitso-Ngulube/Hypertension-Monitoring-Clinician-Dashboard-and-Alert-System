import logging
import re
from contextlib import contextmanager

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

pytestmark = pytest.mark.django_db


@contextmanager
def _security_log_to(path):
    logger = logging.getLogger('security')
    original_handlers = logger.handlers[:]
    original_level = logger.level
    handler = logging.FileHandler(path, encoding='utf-8')
    handler.setLevel(logging.WARNING)
    handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    logger.handlers = [handler]
    logger.setLevel(logging.WARNING)
    try:
        yield path
    finally:
        logger.handlers = original_handlers
        logger.setLevel(original_level)
        handler.close()


def test_failed_login_is_logged(tmp_path):
    User.objects.create_user(
        username='security-login-test',
        email='security-login@example.com',
        password='correct-password',
    )
    log_path = tmp_path / 'security.log'
    with _security_log_to(log_path):
        response = APIClient().post('/api/auth/login/', {
            'username': 'security-login-test',
            'password': 'incorrect-password',
        }, format='json', REMOTE_ADDR='192.0.2.25')

    log_entry = log_path.read_text(encoding='utf-8')
    assert response.status_code == 401
    assert 'security-login-test' in log_entry
    assert 'Failed login' in log_entry
    assert re.search(r'\d{4}-\d{2}-\d{2}', log_entry)


def test_unauthenticated_request_is_logged(tmp_path):
    log_path = tmp_path / 'security.log'
    with _security_log_to(log_path):
        response = APIClient().get('/api/patients/')

    log_entry = log_path.read_text(encoding='utf-8')
    assert response.status_code in (401, 403)
    assert 'Unauthorized request' in log_entry
    assert '/api/patients/' in log_entry


def test_bad_token_is_logged(tmp_path):
    log_path = tmp_path / 'security.log'
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Bearer definitely-invalid-token')
    with _security_log_to(log_path):
        response = client.get('/api/patients/')

    log_entry = log_path.read_text(encoding='utf-8')
    assert response.status_code in (401, 403)
    assert 'Unauthorized request' in log_entry
    assert '/api/patients/' in log_entry
