from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from accounts.permissions import IsClinicianOrAdmin

from .models import Appointment
from .serializers import AppointmentSerializer


class AppointmentAccessPermission(permissions.BasePermission):
    """Allow patients to read their appointments, but only staff to edit them."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role in ['clinician', 'admin']


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [AppointmentAccessPermission]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Appointment.objects.all()
        elif user.role == 'clinician':
            return Appointment.objects.filter(clinician=user)
        else:  # patient
            return Appointment.objects.filter(patient__user=user)
    def perform_create(self, serializer):
        if self.request.user.role not in ['clinician', 'admin']:
            raise PermissionDenied('Only clinicians and admins can create appointments.')
        serializer.save(clinician=self.request.user)
