from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver

from .monitoring import SecurityMonitor


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    username = credentials.get('username', 'unknown')
    meta = getattr(request, 'META', {}) if request else {}
    forwarded_for = meta.get('HTTP_X_FORWARDED_FOR')
    ip = forwarded_for.split(',')[0].strip() if forwarded_for else meta.get(
        'REMOTE_ADDR'
    )
    SecurityMonitor.log_failed_login(username, ip)
