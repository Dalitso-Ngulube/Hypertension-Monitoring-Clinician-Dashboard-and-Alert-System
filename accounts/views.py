from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, ClinicianCreateSerializer, UserSerializer
from accounts.permissions import IsClinicianOrAdmin

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def get_queryset(self):
        return User.objects.all()   # lazy evaluation

class ClinicianCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsClinicianOrAdmin]
    serializer_class = ClinicianCreateSerializer

    def get_queryset(self):
        return User.objects.all()

    def perform_create(self, serializer):
        role = self.request.data.get('role', 'clinician')
        if role not in ['clinician', 'admin']:
            role = 'clinician'
        serializer.save(role=role)

class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsClinicianOrAdmin]

    def get_queryset(self):
        return User.objects.all()

class CurrentUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
