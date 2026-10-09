import pytest
from rest_framework.test import APIRequestFactory

from accounts.permissions import IsClinicianOrAdmin, IsOwnerOrClinician, IsPatient
from tests.factories import AdminFactory, ClinicianFactory, PatientFactory, UserFactory

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('factory,expected', [
    (AdminFactory, True),
    (ClinicianFactory, True),
    (UserFactory, False),
])
def test_clinician_or_admin_permission(factory, expected):
    request = APIRequestFactory().get('/')
    request.user = factory()

    assert IsClinicianOrAdmin().has_permission(request, None) is expected


def test_patient_permission_and_unknown_role_permission():
    request = APIRequestFactory().get('/')
    permission = IsPatient()
    patient = UserFactory(role='patient')
    request.user = patient
    assert permission.has_permission(request, None) is True

    request.user = UserFactory(role='other')
    assert permission.has_permission(request, None) is False


def test_owner_permission_methods_and_roles():
    admin = AdminFactory()
    clinician = ClinicianFactory()
    owner = UserFactory(role='patient')
    stranger = UserFactory(role='patient')
    patient = PatientFactory(user=owner, clinician=clinician)
    permission = IsOwnerOrClinician()
    factory = APIRequestFactory()

    request = factory.get('/')
    request.user = admin
    assert permission.has_object_permission(request, None, patient) is True

    request = factory.get('/')
    request.user = clinician
    assert permission.has_object_permission(request, None, patient) is True

    request = factory.get('/')
    request.user = owner
    assert permission.has_object_permission(request, None, patient) is True

    request = factory.get('/')
    request.user = stranger
    assert permission.has_object_permission(request, None, patient) is False

    request = factory.patch('/')
    request.user = owner
    assert permission.has_object_permission(request, None, patient) is True

    request = factory.delete('/')
    request.user = stranger
    assert permission.has_object_permission(request, None, patient) is False

    request.user = UserFactory(role='unknown')
    assert permission.has_permission(request, None) is False