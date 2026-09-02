from decimal import Decimal

import pytest

from tests.factories import PatientFactory

pytestmark = pytest.mark.django_db

class TestPatientModel:
    def test_str_method(self):
        patient = PatientFactory(first_name="John", last_name="Doe")
        assert str(patient) == "John Doe"

    def test_auto_primary_key(self):
        patient = PatientFactory()
        assert patient.id is not None

    def test_bmi_property(self):
        patient = PatientFactory(height=Decimal('1.75'), weight=Decimal(70))
        assert float(patient.bmi) == 22.9