from rest_framework import serializers
from .models import BPReading

class BPReadingSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.__str__', read_only=True)

    class Meta:
        model = BPReading
        fields = '__all__'
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