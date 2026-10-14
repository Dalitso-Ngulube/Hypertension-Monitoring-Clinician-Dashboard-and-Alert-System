from django.core.management.base import BaseCommand

from alerts.services import AlertEngine
from patients.models import Patient


class Command(BaseCommand):
    help = 'Check all patients for missed BP readings and create alerts.'

    def handle(self, *args, **options):
        created = 0
        for patient in Patient.objects.all():
            if AlertEngine.check_missed_readings(patient):
                created += 1
        self.stdout.write(
            self.style.SUCCESS(f'Created {created} missed-reading alert(s).')
        )
