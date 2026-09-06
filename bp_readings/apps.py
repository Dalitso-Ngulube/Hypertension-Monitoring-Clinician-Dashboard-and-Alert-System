"""
Django app configuration for the blood pressure readings module.

Registers signal handlers for the alert engine.
"""

from django.apps import AppConfig


class BpReadingsConfig(AppConfig):
    name = 'bp_readings'

    def ready(self):
        """Import signals when the app is ready."""
        import bp_readings.signals 
