import pytest
from django.contrib.auth import get_user_model
from accounts.serializers import RegisterSerializer, ClinicianCreateSerializer

User = get_user_model()

pytestmark = pytest.mark.django_db

class TestRegisterSerializer:
    def test_create_patient(self):
        data = {
            'username': 'patient1',
            'password': 'secure123',
            'email': 'p1@example.com',
            'phone_number': '1234567890'
        }
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.role == 'patient'
        assert user.check_password('secure123')

    def test_missing_email_raises(self):
        data = {
            'username': 'patient2',
            'password': 'secure123',
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

class TestClinicianCreateSerializer:
    def test_create_clinician(self):
        data = {
            'username': 'doc1',
            'password': 'docpass',
            'email': 'doc@example.com',
            'role': 'clinician'
        }
        serializer = ClinicianCreateSerializer(data=data)
        assert serializer.is_valid()
        user = serializer.save()
        assert user.role == 'clinician'