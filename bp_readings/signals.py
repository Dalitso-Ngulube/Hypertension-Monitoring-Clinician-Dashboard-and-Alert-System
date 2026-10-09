import logging

from django.db.models.signals import post_save
from django.db import transaction
from django.dispatch import receiver

from alerts.services import AlertEngine

from .models import BPReading

logger = logging.getLogger(__name__)

@receiver(post_save, sender=BPReading)
def run_alert_engine(sender, instance, created, **kwargs):
    """Run alert engine when a BP reading is created or corrected."""
    action = 'created' if created else 'updated'
    logger.info(f"Running alert engine for {action} reading {instance.id}")

    with transaction.atomic():
        AlertEngine.check_crisis(instance)
        AlertEngine.check_trend(instance.patient)
        AlertEngine.check_missed_readings(instance.patient)
