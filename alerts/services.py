from django.utils import timezone
from datetime import timedelta
from .models import Alert
from bp_readings.models import BPReading
from notifications.dispatcher import NotificationDispatcher

class AlertEngine:
    @staticmethod
    def check_crisis(reading):
        if reading.risk_category == 'CRISIS':
            Alert.objects.create(
                patient=reading.patient,
                alert_type='CRISIS',
                severity='CRITICAL',
                message=f'BP {reading.systolic}/{reading.diastolic} – immediate attention required'
            )
    
    @staticmethod
    def check_missed_readings(patient):
        last_reading = patient.bp_readings.first()
        if last_reading and (timezone.now() - last_reading.recorded_at) > timedelta(days=2):
            Alert.objects.create(
                patient=patient,
                alert_type='MISSED_READING',
                severity='MEDIUM',
                message='No BP reading in last 48 hours'
            )
    
    @staticmethod
    def check_trend(patient):
        last_three = patient.bp_readings.all()[:3]
        if len(last_three) == 3:
            # All three elevated or above
            if all(r.risk_category in ['ELEVATED', 'STAGE_1', 'STAGE_2'] for r in last_three):
                Alert.objects.create(
                    patient=patient,
                    alert_type='TRENDING_UP',
                    severity='HIGH',
                    message='Three consecutive elevated readings'
