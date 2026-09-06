from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Patient

User = get_user_model()

@receiver(post_save, sender=User)
def create_patient_for_user(sender, instance, created, **kwargs):
    """Create a Patient profile automatically when a user with role 'patient' is created."""
    if created and instance.role == 'patient':
        Patient.objects.get_or_create(
            user=instance,
            defaults={
                'first_name': instance.first_name or '',
                'last_name': instance.last_name or '',
                'age': 0,
                'gender': '',
                'phone_number': instance.phone_number or '',
                'address': '',
            }
        )