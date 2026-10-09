import pytest
from django.core.exceptions import ValidationError
from rest_framework.test import APIRequestFactory

from core.permissions import IsOwnerOrReadOnly
from core.validators import SpecialCharacterValidator
from tests.factories import PatientFactory, UserFactory


def test_special_character_validator_accepts_and_rejects_passwords():
    validator = SpecialCharacterValidator()

    validator.validate('SecurePassword!123')
    with pytest.raises(ValidationError) as error:
        validator.validate('Password123')

    assert error.value.code == 'password_no_special'
    assert 'special character' in validator.get_help_text()


@pytest.mark.django_db
def test_owner_or_read_only_permission_for_safe_and_write_methods():
    owner = UserFactory(role='patient')
    other = UserFactory(role='patient')
    patient = PatientFactory(user=owner)
    permission = IsOwnerOrReadOnly()
    factory = APIRequestFactory()

    request = factory.get('/')
    request.user = other
    assert permission.has_object_permission(request, None, patient) is True

    request = factory.patch('/')
    request.user = owner
    assert permission.has_object_permission(request, None, patient) is True

    request.user = other
    assert permission.has_object_permission(request, None, patient) is False