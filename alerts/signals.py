from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Alert
from notifications.services import Notifier
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Alert)
def send_alert_notifications(sender, instance, created, **kwargs):
    """Send email/SMS when a new critical alert is created."""
    if not created:
        return
    if instance.severity not in ['CRITICAL', 'HIGH']:
        return

    patient = instance.patient
    clinician = patient.clinician

    if clinician and clinician.email:
        subject = f" ALERT: {instance.severity} – {patient.first_name} {patient.last_name}"
        body = (
            f"Alert: {instance.message}\n\n"
            f"Patient: {patient.first_name} {patient.last_name} (ID: {patient.id})\n"
            f"Severity: {instance.severity}\n"
            f"Time: {instance.created_at}\n\n"
            f"Please log in to VitalTrack for further action."
        )
        Notifier.send_email(clinician.email, subject, body)

    # 2. Notify patient via SMS (if phone number exists)
    if patient.phone_number:
        sms_body = f"VitalTrack Alert: {instance.message}. Please contact your clinician."
        Notifier.send_sms(patient.phone_number, sms_body)

    # 3. Optionally email patient as well
    if patient.user and patient.user.email:
        subject = f"VitalTrack Alert – {patient.first_name} {patient.last_name}"
        body = f"Dear {patient.first_name},\n\nWe've detected an abnormal blood pressure reading. Please contact your clinician immediately.\n\nDetails: {instance.message}\nTime: {instance.created_at}\n\nStay safe,\nYour VitalTrack Team"
        Notifier.send_email(patient.user.email, subject, body)