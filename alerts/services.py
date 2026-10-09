import logging
from datetime import timedelta

from django.utils import timezone

from .models import Alert

logger = logging.getLogger(__name__)

TREND_ALERT_WINDOW_DAYS = 7
MISSED_READING_ALERT_WINDOW_DAYS = 14

class AlertEngine: 
    @staticmethod
    def check_crisis(reading):
        """Create or resolve the crisis alert associated with a reading."""
        unresolved_alerts = Alert.objects.filter(
            reading=reading,
            alert_type='CRISIS',
            is_resolved=False,
        )

        if reading.risk_category == 'CRISIS':
            if not unresolved_alerts.exists():
                Alert.objects.create(
                    reading=reading,
                    patient=reading.patient,
                    alert_type='CRISIS',
                    severity='CRITICAL',
                    message=(
                        f'CRISIS reading: {reading.systolic}/'
                        f'{reading.diastolic} at {reading.recorded_at}'
                    ),
                )
            return True

        unresolved_alerts.update(is_resolved=True, resolved_at=timezone.now())
        return False

    @staticmethod
    def check_trend(patient):
        """Check for 3 consecutive elevated readings."""
        readings = patient.bp_readings.all()[:3]
        if len(readings) == 3:
            risk_categories = [r.risk_category for r in readings]
            if all(c in ['ELEVATED', 'STAGE_1', 'STAGE_2', 'CRISIS'] for c in risk_categories):
                recent_unresolved = Alert.objects.filter(
                    patient=patient,
                    alert_type='TRENDING_UP',
                    is_resolved=False,
                    created_at__gte=(
                        timezone.now()
                        - timedelta(days=TREND_ALERT_WINDOW_DAYS)
                    ),
                ).exists()
                if not recent_unresolved:
                    Alert.objects.create(
                        patient=patient,
                        alert_type='TRENDING_UP',
                        severity='HIGH',
                        message='Three consecutive elevated readings detected',
                    )
                    logger.info(f"Trend alert created for patient {patient.id}")
                return True
        return False

    @staticmethod
    def check_missed_readings(patient):
        """Check if patient has no reading in last 48 hours."""
        last_reading = patient.bp_readings.first()
        if last_reading and (timezone.now() - last_reading.recorded_at) > timedelta(hours=48):
            recent_unresolved = Alert.objects.filter(
                patient=patient,
                alert_type='MISSED_READING',
                is_resolved=False,
                created_at__gte=(
                    timezone.now()
                    - timedelta(days=MISSED_READING_ALERT_WINDOW_DAYS)
                ),
            ).exists()
            if not recent_unresolved:
                Alert.objects.create(
                    patient=patient,
                    alert_type='MISSED_READING',
                    severity='MEDIUM',
                    message='No BP reading recorded in the last 48 hours',
                )
                logger.info(f"Missed reading alert created for patient {patient.id}")
            return True
        return False
