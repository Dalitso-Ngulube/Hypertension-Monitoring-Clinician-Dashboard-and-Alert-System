import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from tests.factories import AdminFactory, UserFactory

pytestmark = pytest.mark.django_db

class TestRegisterView:
    def test_register_success(self):
        client = APIClient()
        url = reverse('register')
        payload = {
            'username': 'newuser',
            'password': 'pass123',
            'email': 'new@example.com',
            'phone_number': '123456'
        }
        response = client.post(url, payload)
        assert response.status_code == 201
        assert response.data['username'] == 'newuser'

class TestClinicianCreateView:
    def test_admin_can_create_clinician(self):
        admin = AdminFactory()
        client = APIClient()
        client.force_authenticate(user=admin)
        url = reverse('create-clinician')
        payload = {
            'username': 'clinician1',
            'password': 'pass123',
            'email': 'clin@example.com',
            'role': 'clinician'
        }
        response = client.post(url, payload)
        assert response.status_code == 201

    def test_non_admin_cannot_create_clinician(self):
        user = UserFactory()
        client = APIClient()
        client.force_authenticate(user=user)
        url = reverse('create-clinician')
        response = client.post(url, {})
        assert response.status_code == 403