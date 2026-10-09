from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from accounts.permissions import IsClinicianOrAdmin
from accounts.permissions import IsOwnerOrClinician
from core.audit import log_action

from .models import (
    Allergy,
    MedicalCondition,
    Medication,
    Patient,
    PatientMedicalHistory,
)
from .serializers import (
    AllergySerializer,
    MedicalConditionSerializer,
    MedicationSerializer,
    PatientMedicalHistorySerializer,
    PatientSerializer,
)


class PatientListCreateView(generics.ListCreateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrClinician]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Patient.objects.all()
        elif user.role == 'clinician':
            return Patient.objects.filter(clinician=user)
        else:  # patient
            return Patient.objects.filter(user=user)

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'admin':
            patient = serializer.save()
        elif user.role == 'clinician':
            patient = serializer.save(clinician=user)
        else:
            raise PermissionDenied("Patients are not allowed to create patient records.")
        log_action(user, 'CREATE', patient, request=self.request)


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrClinician]

    def perform_update(self, serializer):
        patient = serializer.save()
        log_action(
            self.request.user,
            'UPDATE',
            patient,
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


class PatientMedicalHistoryView(generics.RetrieveUpdateAPIView):
    serializer_class = PatientMedicalHistorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrClinician]

    def get_object(self):
        patient_id = self.kwargs.get('patient_id')
        patient = get_object_or_404(Patient, id=patient_id)
        history, created = PatientMedicalHistory.objects.get_or_create(patient=patient)
        return history

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class MedicalConditionListView(generics.ListCreateAPIView):
    queryset = MedicalCondition.objects.all()
    serializer_class = MedicalConditionSerializer
    permission_classes = [IsClinicianOrAdmin]


class AllergyListView(generics.ListCreateAPIView):
    queryset = Allergy.objects.all()
    serializer_class = AllergySerializer
    permission_classes = [IsClinicianOrAdmin]


class MedicationListView(generics.ListCreateAPIView):
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer
    permission_classes = [IsClinicianOrAdmin]