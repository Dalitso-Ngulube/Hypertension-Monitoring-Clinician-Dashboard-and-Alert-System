from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from bp_readings.models import BPReading
from patients.models import Patient
from accounts.permissions import IsOwnerOrClinician


class PatientTrendView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrClinician]

    def get(self, request, patient_id):
        user = request.user
        # Role‑aware lookup
        if user.role == 'admin':
            patient = get_object_or_404(Patient, id=patient_id)
        elif user.role == 'clinician':
            patient = get_object_or_404(Patient, id=patient_id, clinician=user)
        else:  # patient
            patient = get_object_or_404(Patient, id=patient_id, user=user)

        readings = BPReading.objects.filter(patient=patient).order_by('recorded_at')
        data = [{
            "date": r.recorded_at,
            "systolic": r.systolic,
            "diastolic": r.diastolic,
            "risk_category": r.risk_category,
        } for r in readings]
        return Response(data)


class BPTrendView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrClinician]

    def get(self, request, patient_id):
        user = request.user
        if user.role == 'admin':
            patient = get_object_or_404(Patient, id=patient_id)
        elif user.role == 'clinician':
            patient = get_object_or_404(Patient, id=patient_id, clinician=user)
        else:
            patient = get_object_or_404(Patient, id=patient_id, user=user)

        days = request.query_params.get('days', 30)
        start_date = timezone.now() - timedelta(days=int(days))
        readings = (
            BPReading.objects
            .filter(patient=patient, recorded_at__gte=start_date)   # use patient object
            .annotate(date=TruncDate('recorded_at'))
            .values('date')
            .annotate(
                avg_systolic=Avg('systolic'),
                avg_diastolic=Avg('diastolic'),
                count=Count('id')
            )
            .order_by('date')
        )
        data = [{
            "date": item['date'],
            "avg_systolic": item['avg_systolic'],
            "avg_diastolic": item['avg_diastolic'],
            "count": item['count']
        } for item in readings]
        return Response(data)


class AnalyticsSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == 'admin':
            patients = Patient.objects.all()
        elif user.role == 'clinician':
            patients = Patient.objects.filter(clinician=user)
        else:
            patients = Patient.objects.filter(user=user)

        total_patients = patients.count()
        readings = BPReading.objects.filter(patient__in=patients)   
        total_readings = readings.count()
        critical_readings = readings.filter(
            Q(risk_category='CRISIS')
        ).count()
        return Response({
            'total_patients': total_patients,
            'total_readings': total_readings,
            'critical_readings': critical_readings,
        })


class RiskDistributionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == 'admin':
            patients = Patient.objects.all()
        elif user.role == 'clinician':
            patients = Patient.objects.filter(clinician=user)
        else:
            patients = Patient.objects.filter(user=user)

        distribution = (
            BPReading.objects
            .filter(patient__in=patients)  
            .values('risk_category')
            .annotate(count=Count('id'))
        )
        result = {}
        for item in distribution:
            cat = item['risk_category'] or 'UNKNOWN'
            result[cat] = item['count']
        return Response(result)


class RiskScoreView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrClinician]

    def get(self, request, patient_id):
        user = request.user
        if user.role == 'admin':
            patient = get_object_or_404(Patient, id=patient_id)
        elif user.role == 'clinician':
            patient = get_object_or_404(Patient, id=patient_id, clinician=user)
        else:
            patient = get_object_or_404(Patient, id=patient_id, user=user)

        score = self.calculate_risk_score(patient)
        level = "Low" if score < 30 else "Medium" if score < 70 else "High"
        return Response({"score": score, "level": level})

    @staticmethod
    def calculate_risk_score(patient):
        readings = patient.bp_readings.all()[:10]
        if not readings:
            return 0
        crisis_count = sum(1 for r in readings if r.risk_category == 'CRISIS')   # no getattr needed
        stage2_count = sum(1 for r in readings if r.risk_category == 'STAGE_2')
        score = (crisis_count * 10) + (stage2_count * 5)
        return min(score, 100)
