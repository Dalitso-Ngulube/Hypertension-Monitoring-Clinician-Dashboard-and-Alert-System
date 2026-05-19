from django.shortcuts import render

from rest_framework import generics, permissions
from .models import Alert
from .serializers import AlertSerializer
from core.permissions import IsOwnerOrReadOnly

class AlertListCreateView(generics.ListCreateAPIView):
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Alert.objects.filter(patient__user=self.request.user)

class AlertUpdateView(generics.UpdateAPIView):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    http_method_names = ['patch']
