from rest_framework import permissions, viewsets

from accounts.permissions import IsClinicianOrAdmin

from .models import Appointment
from .serializers import AppointmentSerializer


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsClinicianOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Appointment.objects.all()
        elif user.role == 'clinician':
            return Appointment.objects.filter(clinician=user)
        else:  # patient
            return Appointment.objects.filter(patient__user=user)
    def perform_create(self, serializer):
        serializer.save(clinician=self.request.user)
