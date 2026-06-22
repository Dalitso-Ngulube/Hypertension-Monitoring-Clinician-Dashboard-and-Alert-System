from rest_framework import generics, permissions
from .models import Patient
from .serializers import PatientSerializer
from accounts.permissions import IsOwnerOrClinician

class PatientListCreateView(generics.ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrClinician]
    lookup_url_kwarg = 'patient_id'
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Patient.objects.all()
        elif user.role == 'clinician':
            return Patient.objects.filter(clinician=user)
        else:  # patient
            return Patient.objects.filter(user=user)

    def perform_create(self, serializer):

        serializer.save()


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrClinician]