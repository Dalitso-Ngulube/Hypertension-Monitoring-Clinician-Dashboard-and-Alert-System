from rest_framework import serializers
from .models import BPReading


class BPReadingSerializer(serializers.ModelSerializer):

    patient_name = serializers.CharField(
        source='patient.__str__',
        read_only=True
    )

    class Meta:
        model = BPReading

        fields = [
            'id',
            'patient',
            'patient_name',
            'systolic',
            'diastolic',
            'pulse_rate',
            'recorded_at',
            'created_at',
        ]