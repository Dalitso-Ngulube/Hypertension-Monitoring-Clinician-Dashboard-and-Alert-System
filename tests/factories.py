import factory
from factory.django import DjangoModelFactory
from factory import Faker, SubFactory, post_generation
from django.contrib.auth import get_user_model
from patients.models import Patient, PatientMedicalHistory
from bp_readings.models import BPReading
from alerts.models import Alert
from appointments.models import Appointment

User = get_user_model()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = Faker('user_name')
    email = Faker('email')
    password = post_generation(lambda obj, *args, **kwargs: obj.set_password('testpass123'))
    phone_number = Faker('phone_number', locale='en_US')
    role = 'patient'

class ClinicianFactory(UserFactory):
    role = 'clinician'

class AdminFactory(UserFactory):
    role = 'admin'
    is_staff = True
    is_superuser = True

class PatientFactory(DjangoModelFactory):
    class Meta:
        model = Patient
        skip_postgeneration_save = True

    user = SubFactory(UserFactory)
    clinician = SubFactory(ClinicianFactory)
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    age = Faker('random_int', min=18, max=90)

class PatientMedicalHistoryFactory(DjangoModelFactory):
    class Meta:
        model = PatientMedicalHistory

    patient = SubFactory(PatientFactory)
    smoking_status = 'NEVER'
    alcohol_consumption = 'NONE'
    physical_activity = 'SEDENTARY'
    bmi = 24.0

class BPReadingFactory(DjangoModelFactory):
    class Meta:
        model = BPReading
        skip_postgeneration_save = True

    patient = SubFactory(PatientFactory)
    systolic = Faker('random_int', min=90, max=200)
    diastolic = Faker('random_int', min=60, max=120)
    pulse_rate = Faker('random_int', min=50, max=120)
    source = 'MANUAL'

class AlertFactory(DjangoModelFactory):
    class Meta:
        model = Alert
        skip_postgeneration_save = True

    patient = SubFactory(PatientFactory)
    alert_type = 'Warning'
    severity = 'HIGH'
    message = Faker('sentence')
    is_resolved = False

class AppointmentFactory(DjangoModelFactory):
    class Meta:
        model = Appointment

    patient = SubFactory(PatientFactory)
    clinician = SubFactory(ClinicianFactory)
    date = Faker('date_this_year')
    time = Faker('time')
    duration = 30
    reason = Faker('sentence')
    status = 'SCHEDULED'