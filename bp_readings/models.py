from django.db import models
from django.utils import timezone

from core.utils import CLASSIFY_BP_CHOICES, classify_bp
from patients.models import Patient


class BPReading(models.Model):
    class Source(models.TextChoices):
        SMS = "SMS", "SMS"
        API = "API", "API"
        DEVICE = "DEVICE", "Device"
        MANUAL = "MANUAL", "Manual"

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='bp_readings')
    systolic = models.PositiveIntegerField()
    diastolic = models.PositiveIntegerField()
    pulse_rate = models.PositiveIntegerField(null=True, blank=True)
    recorded_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.MANUAL)
    risk_category = models.CharField(max_length=50, choices=CLASSIFY_BP_CHOICES, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.recorded_at:
            self.recorded_at = timezone.now()
        self.risk_category = classify_bp(self.systolic, self.diastolic)
        super().save(*args, **kwargs)

    def _classify_risk(self):
        from core.utils import classify_bp
        return classify_bp(self.systolic, self.diastolic)

    class Meta:
        ordering = ["-recorded_at"]
        indexes = [
            models.Index(fields=['patient']),
            models.Index(fields=['patient', '-recorded_at']),
            models.Index(fields=['recorded_at']),
        ]

    def __str__(self):
        return f"{self.patient} - {self.systolic}/{self.diastolic}"