from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import BPReading
from alerts.models import Alert
from accounts.permissions import IsOwnerOrClinician
from .serializers import BPReadingSerializer

class BPReadingListCreateView(generics.ListCreateAPIView):
    serializer_class = BPReadingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrClinician]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return BPReading.objects.all()
        elif user.role == 'clinician':
            return BPReading.objects.filter(patient__clinician=user)
        else:  # patient
            return BPReading.objects.filter(patient__user=user)

    def perform_create(self, serializer):
        user = self.request.user
        patient = serializer.validated_data.get('patient')

        # Validate patient ownership
        if user.role == 'admin':
            pass
        elif user.role == 'clinician':
            if patient.clinician != user:
                raise PermissionDenied("You can only add readings for your own patients.")
        else:  # patient
            if patient.user != user:
                raise PermissionDenied("You can only add readings for yourself.")

        reading = serializer.save()

        # Create alert only if not already unresolved
        if reading.risk_category in ['CRISIS', 'STAGE_2']:
            Alert.objects.get_or_create(
                patient=reading.patient,
                is_resolved=False,
                alert_type='BP_CRITICAL',
                defaults={
                    'severity': 'CRITICAL' if reading.risk_category == 'CRISIS' else 'HIGH',
                    'message': f"{reading.risk_category} reading: {reading.systolic}/{reading.diastolic} at {reading.recorded_at}",
                }
            )


class BPReadingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BPReading.objects.all()
    serializer_class = BPReadingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrClinician]