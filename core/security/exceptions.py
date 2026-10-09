from rest_framework.views import exception_handler

from .monitoring import SecurityMonitor


def security_exception_handler(exc, context):
    response = exception_handler(exc, context)
    request = context.get('request')

    if response is not None and response.status_code in (401, 403):
        detail = getattr(exc, 'detail', None)
        reason = str(detail) if detail is not None else exc.__class__.__name__
        SecurityMonitor.log_unauthorized(request, reason)

    return response
