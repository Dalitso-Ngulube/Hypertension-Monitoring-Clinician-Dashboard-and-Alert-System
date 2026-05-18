from django.shortcuts import render

from collections import Counter

from rest_framework.views import APIView
from rest_framework.response import Response

from bp_readings.models import BPReading
from patients.models import Patient

from bp_readings.utils import classify_bp

class PatientTrendView(APIView):
    
    def get(self, request, patient_id):

        readings = BPReading.objects.filter(
            patient_id=patient_id
        ).order_by('recorded_at')

        data = []

        for reading in readings:

            data.append({
                'date': reading.recorded_at,
                'systolic': reading.systolic,
                'diastolic': reading.diastolic,
                'risk': classify_bp(
                    reading.systolic,
                    reading.diastolic
                )
            })

        return Response(data)
    
    
class AnalyticsSummaryView(APIView):
    
    def get(self, request):

        total_patients = Patient.objects.count()

        total_readings = BPReading.objects.count()

        critical_readings = BPReading.objects.filter(
            systolic__gte=180
        ).count()

        return Response({
            'total_patients': total_patients,
            'total_readings': total_readings,
            'critical_readings': critical_readings,
        })
        
class RiskDistributionView(APIView):
    
    def get(self, request):

        readings = BPReading.objects.all()

        risks = []

        for reading in readings:

            risk = classify_bp(
                reading.systolic,
                reading.diastolic
            )

            risks.append(risk)

        distribution = Counter(risks)

        return Response(distribution)            
