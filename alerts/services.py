import logging
from datetime import timedelta

from django.utils import timezone

from .models import Alert

logger = logging.getLogger(__name__)

class AlertEngine: 
    @staticmethod
    def check_crisis(reading):
        """Create crisis alert for CRISIS readings."""
        if reading.risk_category == 'CRISIS':
            Alert.objects.get_or_create(
                reading=reading,
                alert_type='CRISIS',
                defaults={
                    'patient': reading.patient,
                    'severity': 'CRITICAL',
                    'message': f'CRISIS reading: {reading.systolic}/{reading.diastolic} at {reading.recorded_at}',
                }
            )
            return True
        return False

    @staticmethod
    def check_trend(patient):
        """Check for 3 consecutive elevated readings."""
        readings = patient.bp_readings.all()[:3]
        if len(readings) == 3:
            risk_categories = [r.risk_category for r in readings]
            if all(c in ['ELEVATED', 'STAGE_1', 'STAGE_2', 'CRISIS'] for c in risk_categories):
                alert, created = Alert.objects.get_or_create(
                    patient=patient,
                    alert_type='TRENDING_UP',
                    defaults={
                        'severity': 'HIGH',
                        'message': 'Three consecutive elevated readings detected',
                    }
                )
                if created:
                    logger.info(f"Trend alert created for patient {patient.id}")
                return True
        return False

    @staticmethod
    def check_missed_readings(patient):
        """Check if patient has no reading in last 48 hours."""
        last_reading = patient.bp_readings.first()
        if last_reading and (timezone.now() - last_reading.recorded_at) > timedelta(hours=48):
            alert, created = Alert.objects.get_or_create(
                patient=patient,
                alert_type='MISSED_READING',
                defaults={
                    'severity': 'MEDIUM',
                    'message': 'No BP reading recorded in the last 48 hours',
                }
            )
            if created:
                logger.info(f"Missed reading alert created for patient {patient.id}")
            return True
        return False
