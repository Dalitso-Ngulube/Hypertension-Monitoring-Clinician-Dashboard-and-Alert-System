from rest_framework import generics, permissions
from .models import BPReading
from .serializers import BPReadingSerializer
from core.services import handle_bp_reading_created
from core.permissions import IsOwnerOrReadOnly

class BPReadingListCreateView(generics.ListCreateAPIView):
    serializer_class = BPReadingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return BPReading.objects.filter(patient__user=self.request.user)

    def perform_create(self, serializer):
        reading = serializer.save()
        handle_bp_reading_created(reading)

class BPReadingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BPReading.objects.all()
    serializer_class = BPReadingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]