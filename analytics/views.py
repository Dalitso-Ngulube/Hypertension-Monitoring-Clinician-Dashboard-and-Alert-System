import csv
from datetime import timedelta

from django.db.models import Avg, Count, Q
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsClinicianOrAdmin, IsOwnerOrClinician
from alerts.models import Alert
from bp_readings.models import BPReading
from patients.models import Patient

from .cds_service import get_cds_recommendations


class PatientTrendView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrClinician]

    def get(self, request, patient_id):
        user = request.user
        if user.role == 'admin':
            patient = get_object_or_404(Patient, id=patient_id)
        elif user.role == 'clinician':
            patient = get_object_or_404(Patient, id=patient_id, clinician=user)
        else:
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
            .filter(patient=patient, recorded_at__gte=start_date)
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
        crisis_count = sum(1 for r in readings if r.risk_category == 'CRISIS')
        stage2_count = sum(1 for r in readings if r.risk_category == 'STAGE_2')
        score = (crisis_count * 10) + (stage2_count * 5)
        return min(score, 100)


class PatientTimeOfDayPatternsView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrClinician]

    def get(self, request, patient_id):
        user = request.user

        if user.role == 'admin':
            patient = get_object_or_404(Patient, id=patient_id)
        elif user.role == 'clinician':
            patient = get_object_or_404(Patient, id=patient_id, clinician=user)
        else:
            patient = get_object_or_404(Patient, id=patient_id, user=user)

        readings = BPReading.objects.filter(patient=patient)

        time_slots = {
            'night': (0, 5),
            'morning': (6, 11),
            'afternoon': (12, 17),
            'evening': (18, 23),
        }

        result = {}
        for slot_name, (hour_start, hour_end) in time_slots.items():
            slot_readings = readings.filter(
                recorded_at__hour__gte=hour_start,
                recorded_at__hour__lte=hour_end
            )
            avg_systolic = slot_readings.aggregate(Avg('systolic'))['systolic__avg']
            avg_diastolic = slot_readings.aggregate(Avg('diastolic'))['diastolic__avg']
            count = slot_readings.count()

            result[slot_name] = {
                'avg_systolic': round(avg_systolic, 1) if avg_systolic else None,
                'avg_diastolic': round(avg_diastolic, 1) if avg_diastolic else None,
                'count': count,
            }

        return Response(result)


class ExportPatientDataCSV(APIView):
    permission_classes = [IsAuthenticated, IsClinicianOrAdmin]

    def get(self, request, patient_id):
        user = request.user

        if user.role == 'admin':
            patient = get_object_or_404(Patient, id=patient_id)
        elif user.role == 'clinician':
            patient = get_object_or_404(Patient, id=patient_id, clinician=user)
        else:
            raise PermissionDenied("You do not have permission to export this patient's data.")

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{patient.first_name}_{patient.last_name}_data.csv"'

        writer = csv.writer(response)

        writer.writerow([
            'Patient ID', 'First Name', 'Last Name', 'Age', 'Gender',
            'Reading Date', 'Systolic', 'Diastolic', 'Pulse Rate',
            'Risk Category', 'Alert Severity', 'Alert Message',
            'Alert Resolved'
        ])

        readings = BPReading.objects.filter(patient=patient).order_by('-recorded_at')
        alerts = Alert.objects.filter(patient=patient)

        for reading in readings:
            day_alerts = alerts.filter(created_at__date=reading.recorded_at.date())
            if day_alerts.exists():
                alert = day_alerts.first()
                alert_severity = alert.severity
                alert_message = alert.message
                alert_resolved = 'Yes' if alert.is_resolved else 'No'
            else:
                alert_severity = 'N/A'
                alert_message = 'No alert'
                alert_resolved = 'N/A'

            writer.writerow([
                patient.id,
                patient.first_name,
                patient.last_name,
                patient.age,
                patient.gender or 'N/A',
                reading.recorded_at.strftime('%Y-%m-%d %H:%M'),
                reading.systolic,
                reading.diastolic,
                reading.pulse_rate or 'N/A',
                reading.risk_category or 'NORMAL',
                alert_severity,
                alert_message,
                alert_resolved,
            ])

        return response


class ExportAllPatientsSummaryCSV(APIView):
    permission_classes = [IsAuthenticated, IsClinicianOrAdmin]

    def get(self, request):
        user = request.user

        if user.role == 'admin':
            patients = Patient.objects.all()
        elif user.role == 'clinician':
            patients = Patient.objects.filter(clinician=user)
        else:
            raise PermissionDenied("You do not have permission to export this data.")

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="patients_summary.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Patient ID', 'First Name', 'Last Name', 'Age', 'Gender',
            'Latest BP (Systolic/Diastolic)', 'Latest Reading Date',
            'Total Readings', 'Unresolved Alerts', 'Risk Category'
        ])

        for patient in patients:
            latest_reading = patient.bp_readings.first()
            total_readings = patient.bp_readings.count()
            unresolved_alerts = patient.alerts.filter(is_resolved=False).count()

            if latest_reading:
                latest_bp = f"{latest_reading.systolic}/{latest_reading.diastolic}"
                latest_date = latest_reading.recorded_at.strftime('%Y-%m-%d %H:%M')
                risk = latest_reading.risk_category or 'NORMAL'
            else:
                latest_bp = 'No readings'
                latest_date = 'N/A'
                risk = 'N/A'

            writer.writerow([
                patient.id,
                patient.first_name,
                patient.last_name,
                patient.age,
                patient.gender or 'N/A',
                latest_bp,
                latest_date,
                total_readings,
                unresolved_alerts,
                risk,
            ])

        return response

class ClinicalDecisionSupportView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrClinician]

    def get(self, request, patient_id):
        user = request.user
        if user.role == 'admin':
            patient = get_object_or_404(Patient, id=patient_id)
        elif user.role == 'clinician':
            patient = get_object_or_404(Patient, id=patient_id, clinician=user)
        else:
            patient = get_object_or_404(Patient, id=patient_id, user=user)

        data = get_cds_recommendations(patient)
        return Response(data)