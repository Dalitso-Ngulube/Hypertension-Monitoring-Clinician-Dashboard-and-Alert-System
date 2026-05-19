from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from bp_readings.models import BPReading
from patients.models import Patient

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