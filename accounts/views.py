from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, ClinicianCreateSerializer, UserSerializer
from accounts.permissions import IsClinicianOrAdmin
from django.contrib.auth.views import (
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView, 
    PasswordResetCompleteView
)
from django.urls import reverse_lazy
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


class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'registration/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'registration/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'
