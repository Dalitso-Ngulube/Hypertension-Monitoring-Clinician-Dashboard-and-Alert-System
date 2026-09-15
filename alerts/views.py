from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from accounts.permissions import IsClinicianOrAdmin, IsOwnerOrClinician

from .models import Alert
from .serializers import AlertSerializer


class AlertListCreateView(generics.ListCreateAPIView):
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrClinician]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Alert.objects.select_related('patient').all()
        elif user.role == 'clinician':
            return Alert.objects.select_related('patient').filter(patient__clinician=user)
        else:  # patient role
            return Alert.objects.select_related('patient').filter(patient__user=user)

    def perform_create(self, serializer):
        user = self.request.user
        patient = serializer.validated_data.get('patient')

        # Permission checks
        if user.role == 'admin':
            pass
        elif user.role == 'clinician':
            if patient.clinician != user:
                raise PermissionDenied("You can only create alerts for your own patients.")
        else:  # patient
            if patient.user != user:
                raise PermissionDenied("You can only create alerts for yourself.")

        # Use get_or_create to avoid duplicates
        alert_type = serializer.validated_data.get('alert_type', 'Warning')
        severity = serializer.validated_data.get('severity')
        message = serializer.validated_data.get('message')

        alert, created = Alert.objects.get_or_create(
            patient=patient,
            is_resolved=False,
            alert_type=alert_type,
            defaults={
                'severity': severity,
                'message': message,
            }
        )
        if not created:
            alert.message = message
            alert.save()


class AlertUpdateView(generics.UpdateAPIView):
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated, IsClinicianOrAdmin]
    http_method_names = ['patch']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Alert.objects.all()
        return Alert.objects.filter(patient__clinician=user)


class UnresolvedAlertsView(generics.ListAPIView):
    """List only unresolved alerts (for clinicians and admins)."""
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated, IsClinicianOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Alert.objects.select_related('patient').filter(is_resolved=False)
        return Alert.objects.select_related('patient').filter(is_resolved=False, patient__clinician=user)