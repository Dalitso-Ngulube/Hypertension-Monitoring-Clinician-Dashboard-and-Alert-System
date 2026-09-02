import datetime
import logging

from django.core.management.base import BaseCommand
from django.utils import timezone

from appointments.models import Appointment
from notifications.services import Notifier

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Send appointment reminders for tomorrow\'s appointments'

    def handle(self, *args, **options):
        tomorrow = timezone.now().date() + datetime.timedelta(days=1)
        appointments = Appointment.objects.filter(date=tomorrow, status='SCHEDULED')

        if not appointments:
            self.stdout.write('No appointments tomorrow.')
            return

        for apt in appointments:
            patient = apt.patient
            clinician = apt.clinician

            # Remind patient via SMS
            if patient.phone_number:
                msg = f"Reminder: You have an appointment with Dr. {clinician.username} tomorrow at {apt.time.strftime('%H:%M')}. Please arrive 10 minutes early."
                Notifier.send_sms(patient.phone_number, msg)

            # Remind clinician via email
            if clinician.email:
                subject = f"Appointment Reminder: {patient.first_name} {patient.last_name}"
                body = f"Dr. {clinician.username},\n\nYou have an appointment with {patient.first_name} {patient.last_name} tomorrow at {apt.time.strftime('%H:%M')}.\n\nReason: {apt.reason or 'Check-up'}"
                Notifier.send_email(clinician.email, subject, body)

            self.stdout.write(f"Reminder sent for appointment {apt.id}")

        self.stdout.write(' Reminders sent.')