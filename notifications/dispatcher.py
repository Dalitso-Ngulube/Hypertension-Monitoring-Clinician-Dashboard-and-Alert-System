from django.core.mail import send_mail

from .models import NotificationLog
from .services import Notifier


class NotificationDispatcher:
    @staticmethod
    def dispatch(alert):
        # Create an in-app notification record
        NotificationLog.objects.create(
            recipient=alert.patient.user,
            channel='push',
            message=alert.message,
            status='pending',
        )

        # Send an email for critical alerts
        if alert.severity == 'CRITICAL':
            send_mail(
                subject=f"CRITICAL: {alert.patient}",
                message=alert.message,
                from_email="alerts@yourhealthapp.com",
                recipient_list=[alert.patient.user.email],
            )

            # Send an SMS if the patient has a phone number
            if alert.patient.phone_number:
                Notifier.send_sms(
                    alert.patient.phone_number,
                    f'Critical alert for {alert.patient.first_name}: '
                    f'{alert.message}',
                )