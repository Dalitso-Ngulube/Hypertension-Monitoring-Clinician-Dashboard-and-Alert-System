# notifications/services.py
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings

class Notifier:
    @staticmethod
    def send_sms(phone_number, message):
        if not phone_number:
            return
        client = Client(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE,
            to=phone_number
        )
    
    @staticmethod
    def send_email(to_email, subject, body):
        message = Mail(
            from_email=settings.DEFAULT_FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            plain_text_content=body
        )
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)