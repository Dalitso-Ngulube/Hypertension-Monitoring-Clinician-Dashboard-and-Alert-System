from rest_framework import serializers
from .models import BPReading

class BPReadingSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='patient.first_name', read_only=True)
    last_name = serializers.CharField(source='patient.last_name', read_only=True)

    class Meta:
        model = BPReading
        fields = ('id', 'patient', 'first_name', 'last_name', 'systolic', 'diastolic', 'pulse_rate', 'recorded_at', 'source', 'risk_category', 'created_at')
        read_only_fields = ('created_at', 'risk_category')

    def validate(self, data):
        systolic = data.get('systolic')
        diastolic = data.get('diastolic')
        if diastolic > systolic:
            raise serializers.ValidationError("Diastolic cannot exceed systolic.")
        if systolic < 50 or systolic > 250:
            raise serializers.ValidationError("Systolic must be between 50 and 250.")
        if diastolic < 30 or diastolic > 200:
            raise serializers.ValidationError("Diastolic must be between 30 and 200.")
        return data

class PatientAddReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BPReading
        fields = ['systolic', 'diastolic', 'pulse_rate']
