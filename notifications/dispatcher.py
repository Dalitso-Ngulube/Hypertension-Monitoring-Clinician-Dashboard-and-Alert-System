from django.core.mail import send_mail
from alerts.services import send_crisis_sms
from .models import Notification

class NotificationDispatcher:
    @staticmethod
    def dispatch(alert):
        # Create an in-app notification record
        Notification.objects.create(
            user=alert.patient.user,
            message=alert.message,
            alert=alert,
            severity=alert.severity
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
                send_crisis_sms(alert.patient.phone_number, alert.patient.first_name)