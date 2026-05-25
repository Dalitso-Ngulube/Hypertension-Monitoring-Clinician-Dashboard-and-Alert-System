from django.db import models
from patients.models import Patient
from core.utils import CLASSIFY_BP_CHOICES

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
    recorded_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.MANUAL)
    risk_category = models.CharField(max_length=50, choices=CLASSIFY_BP_CHOICES, blank=True, null=True)
    def save(self, *args, **kwargs):
        self.risk_category = self._classify_risk()
        super().save(*args, **kwargs)

    def _classify_risk(self):
        if self.systolic >= 180 or self.diastolic >= 120:
            return "CRISIS"
        if self.systolic >= 140 or self.diastolic >= 90:
            return "STAGE_2"
        if self.systolic >= 130 or self.diastolic >= 80:
            return "STAGE_1"
        if self.systolic >= 120:
            return "ELEVATED"
        return "NORMAL"

    class Meta:
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"{self.patient} - {self.systolic}/{self.diastolic}"