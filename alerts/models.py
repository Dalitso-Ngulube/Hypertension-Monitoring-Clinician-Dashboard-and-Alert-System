from django.db import models
from patients.models import Patient

class Alert(models.Model):

    SEVERITY_CHOICES = (
        ('LOW', 'Low'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    )

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    alert_type = models.CharField(max_length=50, null=True, blank=True)
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES
    )

    message = models.TextField()

    is_resolved = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return (
            f"{self.patient} - "
            f"{self.severity}"
        )
