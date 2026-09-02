"""
Django app configuration for the alerts module.

Registers signal handlers for alert notifications.
"""

from django.apps import AppConfig


class AlertsConfig(AppConfig):
    """Configuration for the alerts app."""

    name = 'alerts'

    def ready(self):
        """Import signals when the app is ready."""
        import alerts.signals  # noqa: F401  # pylint: disable=unused-import,import-outside-toplevel
