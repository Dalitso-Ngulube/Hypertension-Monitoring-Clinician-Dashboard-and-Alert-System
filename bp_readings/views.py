from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from accounts.permissions import IsOwnerOrClinician
from patients.models import Patient

from .models import BPReading
from .serializers import BPReadingSerializer, PatientAddReadingSerializer


class BPReadingListCreateView(generics.ListCreateAPIView):
    serializer_class = BPReadingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrClinician]

    def get_queryset(self):
        user = self.request.user
        queryset = BPReading.objects.all()

        # 1. Role‑based base filtering
        if user.role == 'admin':
            queryset = BPReading.objects.all()
        elif user.role == 'clinician':
            queryset = BPReading.objects.filter(patient__clinician=user)
        else:  # patient
            queryset = BPReading.objects.filter(patient__user=user)

        # 2. Filter by specific patient ID (from query param)
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)

        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        patient = serializer.validated_data.get('patient')

        if user.role == 'admin':
            pass
        elif user.role == 'clinician':
            if patient.clinician != user:
                raise PermissionDenied("You can only add readings for your own patients.")
        else:  # patient
            if patient.user != user:
                raise PermissionDenied("You can only add readings for yourself.")

        reading = serializer.save()

class BPReadingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BPReading.objects.all()
    serializer_class = BPReadingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrClinician]


class PatientAddReadingView(generics.CreateAPIView):
    """
    Allow a patient to add their own BP reading.
    They must be logged in and have a patient record.
    """
    serializer_class = PatientAddReadingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'patient':
            raise PermissionDenied("Only patients can add readings here.")

        try:
            patient = Patient.objects.get(user=user)
        except Patient.DoesNotExist:
            raise PermissionDenied("You do not have a patient profile.")

        reading = BPReading(
            patient=patient,
            systolic=serializer.validated_data['systolic'],
            diastolic=serializer.validated_data['diastolic'],
            pulse_rate=serializer.validated_data.get('pulse_rate'),
            source='MANUAL'
        )
        reading.save()
