from rest_framework import generics

from .models import BPReading
from .serializers import BPReadingSerializer
from alerts.models import Alert
from .utils import classify_bp


class BPReadingListCreateView(generics.ListCreateAPIView):
    queryset = BPReading.objects.all()
    serializer_class = BPReadingSerializer

    def perform_create(self, serializer):
        reading = serializer.save()
    

        systolic = reading.systolic
        diastolic = reading.diastolic

        print("VIEW TRIGGERED")
        print(systolic, diastolic)

    
        risk = classify_bp(systolic, diastolic)

        # CRISIS case from classifier
        if risk == "CRISIS":
            Alert.objects.create(
                patient=reading.patient,
                severity="CRITICAL",
                message=f"Crisis BP detected ({systolic}/{diastolic})"
            )

        # fallback rule-based logic 
        elif systolic >= 180 or diastolic >= 120:
            Alert.objects.create(
                patient=reading.patient,
                severity="CRITICAL",
                message=f"Critical BP reading detected: {systolic}/{diastolic}"
            )

        elif systolic >= 140 or diastolic >= 90:
            Alert.objects.create(
                patient=reading.patient,
                severity="HIGH",
                message=f"High BP reading detected: {systolic}/{diastolic}"
            )
            
class BPReadingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BPReading.objects.all()
    serializer_class = BPReadingSerializer            