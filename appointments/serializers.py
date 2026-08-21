from rest_framework import serializers
from .models import Appointment
from patients.serializers import PatientSerializer

class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    patient_id = serializers.IntegerField(source='patient.id', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id',
            'patient',
            'patient_id',
            'patient_name',
            'clinician',
            'date',
            'time',
            'duration',
            'reason',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['clinician', 'created_at', 'updated_at']

    def get_patient_name(self, obj):
        return f"{obj.patient.first_name} {obj.patient.last_name}"