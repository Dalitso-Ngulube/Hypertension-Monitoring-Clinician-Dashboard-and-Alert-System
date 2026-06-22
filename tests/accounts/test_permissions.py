import pytest
from rest_framework.test import APIRequestFactory
from accounts.permissions import IsOwnerOrClinician
from tests.factories import UserFactory, PatientFactory

@pytest.mark.django_db
def test_is_owner_or_clinician():
    # Arrange
    patient_user = UserFactory(role='patient')
    clinician = UserFactory(role='clinician')
    patient = PatientFactory(user=patient_user, clinician=clinician)
    other_user = UserFactory()
    permission = IsOwnerOrClinician()
    request = APIRequestFactory().get('/')

    # Assert: patient can access own patient
    request.user = patient_user
    assert permission.has_object_permission(request, None, patient) is True

    # Assert: clinician can access assigned patients
    request.user = clinician
    assert permission.has_object_permission(request, None, patient) is True

    # Assert: other user cannot access
    request.user = other_user
    assert permission.has_object_permission(request, None, patient) is False