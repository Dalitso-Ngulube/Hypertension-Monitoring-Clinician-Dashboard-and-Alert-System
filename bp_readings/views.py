from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from accounts.permissions import IsOwnerOrClinician
from core.audit import log_action
from patients.models import Patient
from .models import BPReading
from .serializers import BPReadingSerializer, PatientAddReadingSerializer


class BPReadingListCreateView(generics.ListCreateAPIView):
    serializer_class = BPReadingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrClinician]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        user = self.request.user
        base_queryset = BPReading.objects.select_related('patient').only(
            'id', 'systolic', 'diastolic', 'pulse_rate', 'recorded_at',
            'source', 'risk_category', 'created_at',
            'patient__first_name', 'patient__last_name'
        )

        cutoff = timezone.now() - timedelta(days=30)
        base_queryset = base_queryset.filter(recorded_at__gte=cutoff)

        if user.role == 'admin':
            queryset = base_queryset.all()
        elif user.role == 'clinician':
            queryset = base_queryset.filter(patient__clinician=user)
        else:  # patient
            queryset = base_queryset.filter(patient__user=user)

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

        with transaction.atomic():
            reading = serializer.save()
            log_action(user, 'CREATE', reading, request=self.request)


class BPReadingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BPReading.objects.all()
    serializer_class = BPReadingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrClinician]

    def perform_update(self, serializer):
        with transaction.atomic():
            reading = serializer.save()
            log_action(
                self.request.user,
                'UPDATE',
                reading,
                request=self.request,
            )

    def perform_destroy(self, instance):
        log_action(
            self.request.user,
            'DELETE',
            instance,
            request=self.request,
        )
        instance.delete()


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
        with transaction.atomic():
            reading = serializer.save(patient=patient)
            log_action(user, 'CREATE', reading, request=self.request)
