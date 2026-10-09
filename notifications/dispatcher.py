from django.core.mail import send_mail

from .models import NotificationLog
from .services import Notifier


class NotificationDispatcher:
    @staticmethod
    def dispatch(alert):
        if alert.severity not in ('CRITICAL', 'HIGH'):
            return

        patient = alert.patient
        clinician = patient.clinician
        subject = f"ALERT: {alert.severity} – {patient.first_name} {patient.last_name}"
        recipients = []
        if clinician and clinician.email:
            recipients.append((clinician, clinician.email))
        if patient.user and patient.user.email:
            recipients.append((patient.user, patient.user.email))

        for recipient, email in recipients:
            entry = NotificationLog.objects.create(
                recipient=recipient,
                channel='email',
                subject=subject,
                message=alert.message,
                status='pending',
            )
            try:
                sent = send_mail(
                    subject,
                    alert.message,
                    'alerts@yourhealthapp.com',
                    [email],
                    fail_silently=False,
                )
                entry.status = 'sent' if sent else 'failed'
                if not sent:
                    entry.error_message = 'Email backend did not send a message.'
            except Exception as exc:
                entry.status = 'failed'
                entry.error_message = str(exc)
            entry.save(update_fields=['status', 'error_message'])

        if patient.phone_number and patient.user:
            entry = NotificationLog.objects.create(
                recipient=patient.user,
                channel='sms',
                subject=subject,
                message=alert.message,
                status='pending',
            )
            try:
                Notifier.send_sms(
                    patient.phone_number,
                    f'Critical alert for {patient.first_name}: {alert.message}',
                )
                entry.status = 'sent'
            except Exception as exc:
                entry.status = 'failed'
                entry.error_message = str(exc)
            entry.save(update_fields=['status', 'error_message'])