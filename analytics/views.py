from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from bp_readings.models import BPReading
from patients.models import Patient



class PatientTrendView(APIView):
        permission_classes = [IsAuthenticated]

        def get(self, request, patient_id):
            readings = BPReading.objects.filter(
                patient_id=patient_id,
                patient__user=request.user
            ).order_by('recorded_at')

            data = [
                {
                    "date": reading.recorded_at,
                    "systolic": reading.systolic,
                    "diastolic": reading.diastolic,
                    "risk_category": reading.risk_category,
                }
                for reading in readings
            ]

            return Response(data)
class AnalyticsSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        total_patients = Patient.objects.filter(user=user).count()
        readings = BPReading.objects.filter(patient__user=user)
        total_readings = readings.count()
        critical_readings = readings.filter(
            Q(systolic__gte=180) | Q(diastolic__gte=120)
        ).count()
        return Response({
            'total_patients': total_patients,
            'total_readings': total_readings,
            'critical_readings': critical_readings,
        })

class RiskDistributionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        distribution = BPReading.objects.filter(
            patient__user=request.user
        ).values('risk_category').annotate(count=Count('id'))
        return Response({item['risk_category']: item['count'] for item in distribution})
    
   