"""
Seed BP readings so that each patient has exactly 10 readings.

Usage:
    python manage.py seed_bp_readings
    python manage.py seed_bp_readings --readings-per-patient 10
    python manage.py seed_bp_readings --clear
    python manage.py seed_bp_readings --patients 50
"""
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import timezone

from bp_readings.models import BPReading
from patients.models import Patient


# Realistic BP value pools designed so each category appears.
# Format: (systolic, diastolic, weight)
BP_POOL = [
    # NORMAL — 20% of readings
    (110, 70, 5), (115, 72, 4), (118, 74, 4), (116, 76, 4),
    (112, 68, 3),

    # ELEVATED — 20%
    (125, 75, 4), (128, 78, 4), (122, 79, 4), (135, 78, 4),
    (130, 75, 4),

    # STAGE_1 — 25%
    (135, 85, 5), (138, 88, 4), (140, 90, 4),
    (130, 85, 4), (145, 82, 3), (139, 87, 3),

    # STAGE_2 — 25%
    (145, 95, 5), (150, 98, 4), (155, 100, 4),
    (160, 100, 4), (165, 95, 3), (142, 92, 3),

    # CRISIS — 10%
    (185, 125, 3), (190, 130, 2), (200, 120, 2),
    (182, 122, 2), (195, 128, 2),
]


class Command(BaseCommand):
    help = 'Seed 10 BP readings for each patient (default 500 total across 50 patients).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--readings-per-patient',
            type=int,
            default=10,
            help='Number of BP readings per patient (default: 10)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete existing BP readings before seeding',
        )
        parser.add_argument(
            '--patients',
            type=int,
            default=None,
            help='Limit to the first N patients (default: all)',
        )

    def handle(self, *args, **options):
        per_patient = options['readings_per_patient']
        clear = options['clear']
        patient_limit = options['patients']

        if clear:
            deleted, _ = BPReading.objects.all().delete()
            self.stdout.write(self.style.WARNING(
                f'Deleted {deleted} existing BP readings.'
            ))

        patients = list(Patient.objects.all())
        if patient_limit:
            patients = patients[:patient_limit]

        if not patients:
            self.stdout.write(self.style.ERROR(
                'No patients found. Run `python manage.py seed_patients` first.'
            ))
            return

        now = timezone.now()
        weighted_pool = []
        for systolic, diastolic, weight in BP_POOL:
            weighted_pool.extend([(systolic, diastolic)] * weight)

        total_created = 0
        for patient in patients:
            existing = BPReading.objects.filter(patient=patient).count()
            to_create = max(0, per_patient - existing)

            for _ in range(to_create):
                systolic, diastolic = random.choice(weighted_pool)
                recorded_at = now - timedelta(
                    days=random.randint(0, 29),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59),
                )

                BPReading.objects.create(
                    patient=patient,
                    systolic=systolic,
                    diastolic=diastolic,
                    pulse_rate=random.randint(58, 100),
                    recorded_at=recorded_at,
                    source=random.choice([
                        BPReading.Source.MANUAL,
                        BPReading.Source.DEVICE,
                    ]),
                )
                total_created += 1

        self.stdout.write(self.style.SUCCESS(
            f'Created {total_created} BP readings across {len(patients)} patients '
            f'(target: {per_patient} per patient).'
        ))

        summary = (
            BPReading.objects
            .values('risk_category')
            .annotate(n=Count('id'))
            .order_by('risk_category')
        )
        self.stdout.write('\nReadings by category:')
        for row in summary:
            self.stdout.write(
                f"  {row['risk_category'] or 'UNSET':<12} {row['n']}"
            )
