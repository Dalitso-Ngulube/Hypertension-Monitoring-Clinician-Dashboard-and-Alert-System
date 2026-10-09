from alerts.models import Alert
from notifications.services import Notifier

def process_alert(alert_id):
    alert = Alert.objects.get(id=alert_id)
    # Send SMS to patient if crisis
    if alert.alert_type == 'CRISIS' and alert.patient.phone_number:
        Notifier.send_sms(alert.patient.phone_number, alert.message)
    # Send email to clinician
    clinician_email = alert.patient.user.email  # or fetch assigned clinician
    if clinician_email:
        Notifier.send_email(
            clinician_email,
            f'Alert: {alert.alert_type}',
            alert.message,
        )