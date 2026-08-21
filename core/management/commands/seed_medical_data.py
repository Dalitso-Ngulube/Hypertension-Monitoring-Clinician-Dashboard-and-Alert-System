import json
from django.core.management.base import BaseCommand
from patients.models import MedicalCondition, Allergy, Medication

class Command(BaseCommand):
    help = 'Seed medical reference data (conditions, allergies, medications)'

    def handle(self, *args, **options):
        self.stdout.write('Seeding medical reference data...')

        # Medical Conditions
        conditions = [
            {'name': 'Type 2 Diabetes', 'category': 'ENDOCRINE'},
            {'name': 'Chronic Kidney Disease', 'category': 'RENAL'},
            {'name': 'Congestive Heart Failure', 'category': 'CARDIOVASCULAR'},
            {'name': 'Coronary Artery Disease', 'category': 'CARDIOVASCULAR'},
            {'name': 'Atrial Fibrillation', 'category': 'CARDIOVASCULAR'},
            {'name': 'COPD', 'category': 'RESPIRATORY'},
            {'name': 'Asthma', 'category': 'RESPIRATORY'},
            {'name': 'Hypothyroidism', 'category': 'ENDOCRINE'},
            {'name': 'Hyperlipidemia', 'category': 'CARDIOVASCULAR'},
            {'name': 'Stroke', 'category': 'NEUROLOGICAL'},
            {'name': 'Peripheral Artery Disease', 'category': 'CARDIOVASCULAR'},
            {'name': 'Depression', 'category': 'MENTAL'},
            {'name': 'Anxiety', 'category': 'MENTAL'},
            {'name': 'Gout', 'category': 'OTHER'},
            {'name': 'Osteoarthritis', 'category': 'OTHER'},
            {'name': 'Sleep Apnea', 'category': 'RESPIRATORY'},
        ]

        for data in conditions:
            condition, created = MedicalCondition.objects.get_or_create(
                name=data['name'],
                defaults={'category': data['category']}
            )
            if created:
                self.stdout.write(f'  Created condition: {condition.name}')

        # Allergies
        allergies = [
            {'name': 'Penicillin', 'severity': 'SEVERE'},
            {'name': 'Sulfonamides', 'severity': 'MODERATE'},
            {'name': 'Aspirin', 'severity': 'SEVERE'},
            {'name': 'NSAIDs', 'severity': 'MODERATE'},
            {'name': 'ACE Inhibitors', 'severity': 'MODERATE'},
            {'name': 'Statins', 'severity': 'MILD'},
            {'name': 'Beta Blockers', 'severity': 'MODERATE'},
            {'name': 'Latex', 'severity': 'SEVERE'},
            {'name': 'Peanuts', 'severity': 'LIFE_THREATENING'},
            {'name': 'Shellfish', 'severity': 'SEVERE'},
            {'name': 'Eggs', 'severity': 'MODERATE'},
            {'name': 'Milk', 'severity': 'MILD'},
            {'name': 'Soy', 'severity': 'MILD'},
            {'name': 'Wheat', 'severity': 'MILD'},
        ]

        for data in allergies:
            allergy, created = Allergy.objects.get_or_create(
                name=data['name'],
                defaults={'severity': data['severity']}
            )
            if created:
                self.stdout.write(f' Created allergy: {allergy.name}')

        # Medications
        medications = [
            {'name': 'Lisinopril', 'category': 'ACE_INHIBITOR', 'generic_name': 'Lisinopril'},
            {'name': 'Amlodipine', 'category': 'CALCIUM_CHANNEL', 'generic_name': 'Amlodipine'},
            {'name': 'Losartan', 'category': 'ARB', 'generic_name': 'Losartan'},
            {'name': 'Hydrochlorothiazide', 'category': 'DIURETIC', 'generic_name': 'Hydrochlorothiazide'},
            {'name': 'Metoprolol', 'category': 'BETA_BLOCKER', 'generic_name': 'Metoprolol'},
            {'name': 'Atenolol', 'category': 'BETA_BLOCKER', 'generic_name': 'Atenolol'},
            {'name': 'Enalapril', 'category': 'ACE_INHIBITOR', 'generic_name': 'Enalapril'},
            {'name': 'Valsartan', 'category': 'ARB', 'generic_name': 'Valsartan'},
            {'name': 'Furosemide', 'category': 'DIURETIC', 'generic_name': 'Furosemide'},
            {'name': 'Spironolactone', 'category': 'DIURETIC', 'generic_name': 'Spironolactone'},
            {'name': 'Atorvastatin', 'category': 'STATIN', 'generic_name': 'Atorvastatin'},
            {'name': 'Rosuvastatin', 'category': 'STATIN', 'generic_name': 'Rosuvastatin'},
            {'name': 'Metformin', 'category': 'ANTIDIABETIC', 'generic_name': 'Metformin'},
            {'name': 'Insulin Glargine', 'category': 'ANTIDIABETIC', 'generic_name': 'Insulin Glargine'},
            {'name': 'Warfarin', 'category': 'ANTICOAGULANT', 'generic_name': 'Warfarin'},
            {'name': 'Apixaban', 'category': 'ANTICOAGULANT', 'generic_name': 'Apixaban'},
        ]

        for data in medications:
            medication, created = Medication.objects.get_or_create(
                name=data['name'],
                defaults={
                    'generic_name': data['generic_name'],
                    'category': data['category']
                }
            )
            if created:
                self.stdout.write(f' Created medication: {medication.name}')

        self.stdout.write(self.style.SUCCESS(' Medical reference data seeded successfully!'))