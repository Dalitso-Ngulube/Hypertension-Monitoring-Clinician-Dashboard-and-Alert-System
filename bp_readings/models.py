from django.db import models
from patients.models import Patient


class BPReading(models.Model):

    class Source(models.TextChoices):
        SMS = "SMS", "SMS"
        API = "API", "API"
        DEVICE = "DEVICE", "Device"
        MANUAL = "MANUAL", "Manual"

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='bp_readings'
    )

    systolic = models.PositiveIntegerField()
    diastolic = models.PositiveIntegerField()

    pulse_rate = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    
    recorded_at = models.DateTimeField(auto_now_add=True)

    
    created_at = models.DateTimeField(auto_now_add=True)

    source = models.CharField(
        max_length=10,
        choices=Source.choices,
        default=Source.MANUAL
    )

    class Meta:
        ordering = ["-recorded_at"]

    def __str__(self):
        return f"{self.patient} - {self.systolic}/{self.diastolic}"