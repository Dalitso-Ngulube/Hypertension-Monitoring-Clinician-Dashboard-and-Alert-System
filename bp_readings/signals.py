import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from alerts.services import AlertEngine

from .models import BPReading

logger = logging.getLogger(__name__)

@receiver(post_save, sender=BPReading)
def run_alert_engine(sender, instance, created, **kwargs):
    """Run alert engine when a new BP reading is created."""
    if not created:
        return

    logger.info(f"Running alert engine for reading {instance.id}")

    AlertEngine.check_crisis(instance)
    AlertEngine.check_trend(instance.patient)
    AlertEngine.check_missed_readings(instance.patient)
