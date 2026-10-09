import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from notifications.dispatcher import NotificationDispatcher

from .models import Alert

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Alert)
def send_alert_notifications(sender, instance, created, **kwargs):
    """Dispatch and persist notification attempts for new severe alerts."""
    if not created or instance.severity not in ('CRITICAL', 'HIGH'):
        return

    try:
        NotificationDispatcher.dispatch(instance)
    except Exception:
        logger.exception('Failed to dispatch alert notifications for %s', instance.pk)