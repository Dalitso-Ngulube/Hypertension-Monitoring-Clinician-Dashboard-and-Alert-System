from rest_framework import serializers
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Patient

        fields = [
            'id',
            'first_name',
            'last_name',
            'age',
            'gender',
            'phone_number',
            'address',
            'created_at',
            'updated_at',
            'user',
        ]
        read_only_fields = ('user',)