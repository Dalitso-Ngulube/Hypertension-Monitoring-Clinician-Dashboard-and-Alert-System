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

        if user.role == 'admin':
            queryset = BPReading.objects.all()
        elif user.role == 'clinician':
            queryset = BPReading.objects.filter(patient__clinician=user)
        else:  # patient
            queryset = BPReading.objects.filter(patient__user=user)

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

        serializer.save()


class BPReadingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BPReading.objects.all()
    serializer_class = BPReadingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrClinician]


class PatientAddReadingView(generics.CreateAPIView):
    """
    Allow a patient to add their own BP reading.
    Auto-creates a Patient profile if one does not exist.
    """
    serializer_class = PatientAddReadingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrClinician]

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'patient':
            raise PermissionDenied("Only patients can add readings here.")

        # Get or create the patient profile
        patient, created = Patient.objects.get_or_create(
            user=user,
            defaults={
                'first_name': user.first_name or user.username,
                'last_name': '',
                'age': 0,
                'gender': '',
                'phone_number': getattr(user, 'phone_number', ''),
                'address': '',
            }
        )

        # Save the reading with the patient
        serializer.save(patient=patient)
