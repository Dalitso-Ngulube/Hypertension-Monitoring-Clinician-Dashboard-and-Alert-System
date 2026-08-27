import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from patients.models import (
    Patient, PatientMedicalHistory, MedicalCondition,
    Allergy, Medication
)
from bp_readings.models import BPReading
from alerts.models import Alert

User = get_user_model()

FIRST_NAMES = [
    'James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer',
    'Michael', 'Linda', 'William', 'Elizabeth', 'David', 'Barbara',
    'Richard', 'Susan', 'Joseph', 'Jessica', 'Thomas', 'Sarah',
    'Charles', 'Karen', 'Christopher', 'Nancy', 'Daniel', 'Lisa',
    'Matthew', 'Betty', 'Anthony', 'Helen', 'Mark', 'Sandra',
    'Donald', 'Donna', 'Steven', 'Carol', 'Paul', 'Ruth',
    'Andrew', 'Sharon', 'Joshua', 'Michelle', 'Kenneth', 'Laura',
    'Kevin', 'Sarah', 'Brian', 'Kimberly', 'George', 'Deborah',
    'Timothy', 'Emily', 'Ronald', 'Amanda', 'Edward', 'Melissa',
    'Jason', 'Stephanie', 'Jeffrey', 'Rebecca', 'Ryan', 'Shirley',
    'Jacob', 'Amy', 'Gary', 'Angela', 'Nicholas', 'Anna',
    'Eric', 'Brenda', 'Jonathan', 'Pamela', 'Stephen', 'Nicole',
    'Larry', 'Emma', 'Justin', 'Samantha', 'Scott', 'Katherine',
    'Brandon', 'Christine', 'Benjamin', 'Debra', 'Samuel', 'Rachel',
    'Raymond', 'Carolyn', 'Gregory', 'Janet', 'Frank', 'Catherine',
    'Patrick', 'Maria', 'Alexander', 'Heather', 'Jack', 'Diane',
    'Dennis', 'Ruth', 'Jerry', 'Julie', 'Tyler', 'Joyce',
    'Aaron', 'Virginia', 'Grace', 'Peter', 'Alice', 'Henry',
    'Rose', 'George', 'Joy', 'Emanuel', 'Victoria', 'Paul'
]

LAST_NAMES = [
    'Banda', 'Phiri', 'Mwansa', 'Mulenga', 'Mwanza', 'Tembo',
    'Mwape', 'Sikazwe', 'Mwenya', 'Mumba', 'Mwila', 'Chanda',
    'Mwale', 'Bwalya', 'Kaluba', 'Mushiba', 'Chilufya', 'Mukuka',
    'Mpundu', 'Ngoma', 'Chibwe', 'Kasonde', 'Mukwato', 'Chishimba',
    'Miti', 'Sinkala', 'Mushinge', 'Musonda', 'Chitambo', 'Moyo',
    'Nkhoma', 'Kabwe', 'Mukwala', 'Simwanza', 'Mwanakatwe',
    'Chikwanda', 'Mwakalombe', 'Mushota', 'Kapindula', 'Nyirenda',
    'Mwamba', 'Chisanga', 'Chileshe', 'Mukosha', 'Mweemba',
    'Mwiinga', 'Sichilima', 'Mukonka', 'Chansa', 'Hachamba',
    'Mwanawasa', 'Mambilima', 'Chimumbwa', 'Muyunda', 'Chitambala',
    'Simutowe', 'Mushala', 'Kalinga', 'Mulonda',
    'Chivunda', 'Muyenga', 'Kapembwa', 'Simpasa', 'Mukena',
    'Chomba', 'Sikapizye', 'Zulu', 'Mthembu', 'Dlamini',
    'Ndlovu', 'Ncube', 'Sibanda', 'Mkhize', 'Mhlongo',
    'Ngulube', 'Kalunga', 'Chinoyi'
]

STREET_NAMES = [
    'Main', 'Church', 'Hospital', 'Market', 'Freedom', 'Independence',
    'Nkrumah', 'Kenyatta', 'Moi', 'Mandela', 'Kaunda', 'Lumumba',
    'Chiluba', 'Kafue', 'Zambezi', 'Victoria', 'Mosi-oa-Tunya',
    'Burma', 'Mutaba', 'Serenje', 'Mpika', 'Kasama'
]

class Command(BaseCommand):
    help = 'Generates simulated patient data with Zambian names and 3-5 BP readings each.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of patients to generate (default: 50)'
        )
        parser.add_argument(
            '--clinician',
            type=str,
            default='clinician1',
            help='Clinician username to assign patients to (default: clinician1)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing patients and readings before seeding'
        )
        parser.add_argument(
            '--readings',
            type=int,
            default=0,
            help='Exact number of readings per patient (default: random 3-5)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Maximum age of readings in days (default: 30)'
        )

    def handle(self, *args, **options):
        count = options['count']
        clinician_username = options['clinician']
        clear_existing = options['clear']
        specified_readings = options['readings']
        days = options['days']

        if clear_existing:
            self.stdout.write('Clearing existing patients, readings, and alerts...')
            Patient.objects.all().delete()
            BPReading.objects.all().delete()
            Alert.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared.'))

        clinician, created = User.objects.get_or_create(
            username=clinician_username,
            defaults={
                'email': f'{clinician_username}@hospital.com',
                'role': 'clinician',
                'is_staff': True,
            }
        )
        if created:
            clinician.set_password('testpass123')
            clinician.save()
            self.stdout.write(self.style.SUCCESS(f'Created clinician: {clinician_username} (password: testpass123)'))
        else:
            self.stdout.write(f'Using existing clinician: {clinician_username}')

        conditions = list(MedicalCondition.objects.all())
        allergies = list(Allergy.objects.all())
        medications = list(Medication.objects.all())

        if not conditions:
            self.stdout.write(self.style.WARNING('No medical conditions found. Run seed_medical_data first.'))
            return

        patients_created = 0
        total_readings = 0

        for i in range(count):
            first_name = random.choice(FIRST_NAMES)
            last_name = random.choice(LAST_NAMES)
            age = random.randint(25, 85)
            gender = random.choice(['M', 'F'])
            phone = f'096{random.randint(1000000, 9999999)}'
            street = random.choice(STREET_NAMES)
            address = f"{random.randint(1, 999)} {street} Lusaka"   # All patients in Lusaka

            height = round(random.uniform(1.50, 1.95), 2)
            weight = round(random.uniform(50, 120), 1)

            patient = Patient.objects.create(
                clinician=clinician,
                first_name=first_name,
                last_name=last_name,
                age=age,
                gender=gender,
                phone_number=phone,
                address=address,
                height=height,
                weight=weight,
            )

            history, _ = PatientMedicalHistory.objects.get_or_create(patient=patient)

            if conditions:
                selected_conditions = random.sample(conditions, random.randint(1, 3))
                history.conditions.add(*selected_conditions)

            if allergies and random.random() < 0.4:
                selected_allergies = random.sample(allergies, random.randint(1, 2))
                history.allergies.add(*selected_allergies)

            if medications:
                selected_meds = random.sample(medications, random.randint(1, 2))
                history.current_medications.add(*selected_meds)

            history.has_diabetes = random.random() < 0.2
            history.has_kidney_disease = random.random() < 0.1
            history.has_heart_disease = random.random() < 0.15
            history.has_stroke_history = random.random() < 0.05

            smoking_options = ['NEVER', 'FORMER', 'CURRENT']
            history.smoking_status = random.choice(smoking_options)
            if history.smoking_status == 'CURRENT':
                history.smoking_pack_years = random.randint(1, 40)

            alcohol_options = ['NONE', 'LIGHT', 'MODERATE', 'HEAVY']
            history.alcohol_consumption = random.choice(alcohol_options)

            activity_options = ['SEDENTARY', 'LIGHT', 'MODERATE', 'ACTIVE']
            history.physical_activity = random.choice(activity_options)

            history.diet_description = random.choice([
                'Balanced diet', 'High salt intake', 'DASH diet', 'Vegetarian',
                'High processed foods', 'Mediterranean diet', 'Traditional Zambian diet',
                'High carbohydrate diet', 'Low fat diet'
            ])

            history.family_history_hypertension = random.random() < 0.3
            history.family_history_diabetes = random.random() < 0.15
            history.family_history_heart_disease = random.random() < 0.2
            history.family_history_stroke = random.random() < 0.1

            bmi = patient.bmi
            if bmi is not None:
                history.bmi = round(bmi, 1)
            history.save()

            if specified_readings:
                num_readings = specified_readings
            else:
                num_readings = random.randint(3, 5)

            for _ in range(num_readings):
                rand = random.random()
                if rand < 0.50:
                    systolic = random.randint(105, 130)
                    diastolic = random.randint(65, 82)
                elif rand < 0.75:
                    systolic = random.randint(125, 150)
                    diastolic = random.randint(78, 92)
                elif rand < 0.90:
                    systolic = random.randint(140, 170)
                    diastolic = random.randint(90, 108)
                else:
                    systolic = random.randint(180, 220)
                    diastolic = random.randint(110, 135)

                pulse = random.randint(60, 100)
                offset = random.randint(0, days)
                random_time = timezone.now() - timedelta(days=offset)
                random_time = random_time.replace(
                    hour=random.randint(6, 20),
                    minute=random.randint(0, 59),
                    second=0,
                    microsecond=0
                )

                BPReading.objects.create(
                    patient=patient,
                    systolic=systolic,
                    diastolic=diastolic,
                    pulse_rate=pulse,
                    recorded_at=random_time,
                    source='MANUAL',
                )
                total_readings += 1

            patients_created += 1
            if patients_created % 20 == 0:
                self.stdout.write(f'   Generated {patients_created}/{count} patients...')

        self.stdout.write(self.style.SUCCESS('\nSeeding complete!'))
        self.stdout.write(f'   Patients created: {patients_created}')
        self.stdout.write(f'   Total readings: {total_readings}')
        self.stdout.write(f'   Average readings per patient: {total_readings / patients_created if patients_created else 0:.1f}')

        alerts_count = Alert.objects.count()
        self.stdout.write(f'   Total alerts generated: {alerts_count}')

        self.stdout.write('\nLogin credentials:')
        self.stdout.write(f'   Username: {clinician_username}')
        self.stdout.write(f'   Password: testpass123')