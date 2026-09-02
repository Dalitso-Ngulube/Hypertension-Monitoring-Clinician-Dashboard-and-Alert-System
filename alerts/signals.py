import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.services import Notifier

from .models import Alert

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
        subject = f"ALERT: {instance.severity} – {patient.first_name} {patient.last_name}"
        body = (
            f"Alert: {instance.message}\n\n"
            f"Patient: {patient.first_name} {patient.last_name} (ID: {patient.id})\n"
            f"Severity: {instance.severity}\n"
            f"Time: {instance.created_at}\n\n"
            f"Please log in to VitalTrack for further action."
        )
        try:
            Notifier.send_email(clinician.email, subject, body)
            logger.info(f"Email sent to clinician {clinician.email}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")

    if patient.phone_number:
        sms_body = f"VitalTrack Alert: {instance.message}. Please contact your clinician."
        try:
            Notifier.send_sms(patient.phone_number, sms_body)
            logger.info(f"SMS sent to {patient.phone_number}")
        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")

    if patient.user and patient.user.email:
        subject = f"VitalTrack Alert – {patient.first_name} {patient.last_name}"
        body = (
            f"Dear {patient.first_name},\n\n"
            f"We've detected an abnormal blood pressure reading. "
            f"Please contact your clinician immediately.\n\n"
            f"Details: {instance.message}\n"
            f"Time: {instance.created_at}\n\n"
            f"Stay safe,\nYour VitalTrack Team"
        )
        try:
            Notifier.send_email(patient.user.email, subject, body)
            logger.info(f"Email sent to patient {patient.user.email}")
        except Exception as e:
            logger.error(f"Failed to send patient email: {e}")