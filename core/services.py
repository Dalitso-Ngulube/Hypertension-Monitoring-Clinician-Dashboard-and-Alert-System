import logging

from alerts.models import Alert
from bp_readings.models import BPReading

from .utils import classify_bp

logger = logging.getLogger(__name__)

def create_alert_for_reading(reading: BPReading):
    risk = classify_bp(reading.systolic, reading.diastolic)
    if risk == "CRISIS":
        severity = "CRITICAL"
        message = f"Crisis BP detected ({reading.systolic}/{reading.diastolic})"
    elif reading.systolic >= 180 or reading.diastolic >= 120:
        severity = "CRITICAL"
        message = f"Critical BP reading: {reading.systolic}/{reading.diastolic}"
    elif reading.systolic >= 140 or reading.diastolic >= 90:
        severity = "HIGH"
        message = f"High BP reading: {reading.systolic}/{reading.diastolic}"
    else:
        return

    Alert.objects.create(
        patient=reading.patient,
        severity=severity,
        message=message
    )
    logger.info(f"Alert created for patient {reading.patient.id}: {severity}")

def handle_bp_reading_created(reading: BPReading):
    reading.risk_category = classify_bp(reading.systolic, reading.diastolic)
    reading.save(update_fields=['risk_category'])
    create_alert_for_reading(reading)