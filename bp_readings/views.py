from rest_framework import generics

from .models import BPReading
from .serializers import BPReadingSerializer
from alerts.models import Alert


class BPReadingListCreateView(generics.ListCreateAPIView):
    queryset = BPReading.objects.all()
    serializer_class = BPReadingSerializer

    def perform_create(self, serializer):
        reading = serializer.save()

        systolic = reading.systolic
        diastolic = reading.diastolic

        print("VIEW TRIGGERED")
        print(systolic, diastolic)

        # Critical alert
        if systolic >= 180 or diastolic >= 120:
            print("CREATING CRITICAL ALERT")

            Alert.objects.create(
                patient=reading.patient,
                severity='CRITICAL',
                message=f'Critical BP reading detected: {systolic}/{diastolic}'
            )

        # High BP alert
        elif systolic >= 140 or diastolic >= 90:
            print("CREATING HIGH ALERT")

            Alert.objects.create(
                patient=reading.patient,
                severity='HIGH',
                message=f'High BP reading detected: {systolic}/{diastolic}'
            )


class BPReadingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BPReading.objects.all()
    serializer_class = BPReadingSerializer