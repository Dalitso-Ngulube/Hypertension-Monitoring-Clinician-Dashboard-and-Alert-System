import logging

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger('security')

class SecurityMonitor:
    """
    Centralized security monitoring and alerting.
    Logs suspicious activities and sends email alerts.
    """

    @staticmethod
    def log_suspicious(user, action, details=None, request=None):
        """
        Log a suspicious activity and notify admins.

        Args:
            user: Django User object (or None)
            action: string description of the action
            details: dict with extra context
            request: HttpRequest object (optional, for IP/user-agent)
        """
        if details is None:
            details = {}

        # Add IP if request provided
        if request:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            details['ip'] = ip
            details['user_agent'] = request.META.get('HTTP_USER_AGENT', '')

        # Log to security logger
        log_message = f'[SECURITY] User: {user}, Action: {action}, Details: {details}'
        logger.warning(log_message)

        # Send email alert to admins
        admin_emails = getattr(settings, 'ADMIN_EMAILS', [])
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'security@yourhealthapp.com')

        if admin_emails:
            subject = f' Security Alert: {action}'
            message = f"""
Security Alert Detected

User: {user}
Action: {action}
Details: {details}
Timestamp: {timezone.now()}

Please investigate immediately.
            """
            try:
                send_mail(
                    subject,
                    message,
                    from_email,
                    admin_emails,
                    fail_silently=False,
                )
            except Exception as e:
                logger.error(f'Failed to send security alert email: {e}')

    @staticmethod
    def log_login_attempt(username, success, ip=None, user_agent=None):
        """Log login attempts (successful or failed)."""
        details = {'username': username, 'success': success}
        if ip:
            details['ip'] = ip
        if user_agent:
            details['user_agent'] = user_agent

        if success:
            logger.info(f'Successful login: username={username}, ip={ip}')
        else:
            logger.warning(f'Failed login attempt: username={username}, ip={ip}')


    @staticmethod
    def log_api_access(user, method, path, status_code, request=None):
        """Log API access for auditing."""
        details = {
            'method': method,
            'path': path,
            'status_code': status_code,
        }
        if request:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            details['ip'] = ip

        logger.info(f'API Access: user={user}, {method} {path} -> {status_code}')

        # Log suspicious status codes
        if status_code >= 400:
            pass

    @staticmethod
    def log_data_access(user, resource_type, resource_id, action='view'):
        """Log when sensitive data is accessed."""
        logger.info(
            f'Data Access: user={user}, {action} {resource_type} (id={resource_id})'
        )
