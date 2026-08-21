import logging
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client

logger = logging.getLogger(__name__)

class Notifier:
    @staticmethod
    def send_sms(phone_number, message):
        """Send SMS via Twilio (or log in development)."""
        if not phone_number:
            return
        if settings.DEBUG:
            logger.info(f"[SMS] To: {phone_number} | {message}")
            return
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
        except Exception as e:
            logger.error(f"SMS failed to {phone_number}: {e}")

    @staticmethod
    def send_email(to_email, subject, message):
        """Send email via Django's email backend (or console in DEBUG)."""
        if not to_email:
            return
        if settings.DEBUG:
            logger.info(f"[EMAIL] To: {to_email} | Subject: {subject} | {message}")
            return
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email])
        except Exception as e:
            logger.error(f"Email failed to {to_email}: {e}")