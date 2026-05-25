from django.contrib import admin
from .models import BPReading

@admin.register(BPReading)
class BPReadingAdmin(admin.ModelAdmin):
    list_display = ('patient', 'systolic', 'diastolic', 'recorded_at', 'risk_category')
    list_filter = ('patient', 'risk_category')
    search_fields = ('patient__first_name', 'patient__last_name')
