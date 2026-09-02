from django.core.management.base import BaseCommand

from alerts.services import AlertEngine
from patients.models import Patient


class Command(BaseCommand):
    def handle(self, *args, **options):
        for patient in Patient.objects.all():
            AlertEngine.check_missed_readings(patient)