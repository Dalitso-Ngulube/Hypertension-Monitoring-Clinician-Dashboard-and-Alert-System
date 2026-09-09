
from django.test import TestCase

from patients.models import Patient
from .serializers import BPReadingSerializer


class BPReadingSerializerTests(TestCase):
	def test_clinician_payload_can_omit_timestamp_and_pulse_rate(self):
		patient = Patient.objects.create(first_name='Test', last_name='Patient')
		serializer = BPReadingSerializer(data={
			'patient': patient.pk,
			'systolic': 120,
			'diastolic': 80,
		})

		self.assertTrue(serializer.is_valid(), serializer.errors)
		self.assertIsNotNone(serializer.validated_data['recorded_at'])
