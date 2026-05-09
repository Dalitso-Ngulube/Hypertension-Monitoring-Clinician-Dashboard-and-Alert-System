from rest_framework import serializers
from .models import Alert


class AlertSerializer(serializers.ModelSerializer):

    patient_name = serializers.CharField(
        source='patient.__str__',
        read_only=True
    )

    class Meta:
        model = Alert

        fields = [
            'id',
            'patient',
            'patient_name',
            'severity',
            'message',
            'is_resolved',
            'created_at',
        ]