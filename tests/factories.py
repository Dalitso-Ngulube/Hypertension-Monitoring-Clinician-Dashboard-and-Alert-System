import factory
from factory.django import DjangoModelFactory
from factory import Faker, SubFactory, post_generation
from django.contrib.auth import get_user_model
from patients.models import Patient
from bp_readings.models import BPReading
from alerts.models import Alert

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