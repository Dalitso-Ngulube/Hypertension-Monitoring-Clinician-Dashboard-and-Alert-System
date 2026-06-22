import pytest
from tests.factories import PatientFactory, UserFactory

pytestmark = pytest.mark.django_db

class TestPatientModel:
    def test_str_method(self):
        patient = PatientFactory(first_name="John", last_name="Doe")
        assert str(patient) == "John Doe"

    def test_auto_primary_key(self):
        patient = PatientFactory()
        assert patient.id is not None