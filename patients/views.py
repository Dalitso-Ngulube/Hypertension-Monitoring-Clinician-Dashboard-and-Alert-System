from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from .models import Patient, PatientMedicalHistory, MedicalCondition, Allergy, Medication
from .serializers import (
   PatientSerializer, PatientDetailSerializer, PatientMedicalHistorySerializer,
   MedicalConditionSerializer, AllergySerializer, MedicationSerializer
)
from accounts.permissions import IsOwnerOrClinician

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
            serializer.save()
        elif user.role == 'clinician':
            serializer.save(clinician=user)
        else:
            raise PermissionDenied("Patients are not allowed to create patient records.")

class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrClinician]
class PatientMedicalHistoryView(generics.RetrieveUpdateAPIView):
    """Get or update a patient's medical history"""
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


class MedicalConditionListView(generics.ListAPIView):
    """List all medical conditions"""
    queryset = MedicalCondition.objects.all()
    serializer_class = MedicalConditionSerializer
    permission_classes = [permissions.IsAuthenticated]


class AllergyListView(generics.ListAPIView):
    """List all allergies"""
    queryset = Allergy.objects.all()
    serializer_class = AllergySerializer
    permission_classes = [permissions.IsAuthenticated]


class MedicationListView(generics.ListAPIView):
    """List all medications"""
    queryset = Medication.objects.all()
    serializer_class = MedicationSerializer
    permission_classes = [permissions.IsAuthenticated]