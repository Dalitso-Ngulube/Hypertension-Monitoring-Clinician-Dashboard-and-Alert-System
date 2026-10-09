from core.models import AuditLog


def log_action(user, action, target, metadata=None, request=None):
    """Persist an audit event for a user action on a model instance."""
    meta = getattr(request, 'META', {}) if request else {}
    forwarded_for = meta.get('HTTP_X_FORWARDED_FOR')
    ip_address = forwarded_for.split(',')[0].strip() if forwarded_for else meta.get(
        'REMOTE_ADDR'
    )
    return AuditLog.objects.create(
        user=user if getattr(user, 'is_authenticated', False) else None,
        action=action,
        resource_type=target._meta.label,
        resource_id=getattr(target, 'pk', None),
        ip_address=ip_address,
        user_agent=meta.get('HTTP_USER_AGENT', ''),
        details=metadata or {},
    )