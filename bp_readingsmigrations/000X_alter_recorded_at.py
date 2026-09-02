from django.db import migrations, models
from django.utils import timezone


def set_default_recorded_at(apps, schema_editor):
    BPReading = apps.get_model('bp_readings', 'BPReading')
    for reading in BPReading.objects.all():
        if not reading.recorded_at:
            reading.recorded_at = reading.created_at or timezone.now()
            reading.save()

class Migration(migrations.Migration):
    dependencies = [
        ('Alter field recorded_at on bpreading') 
    ]

    operations = [
        migrations.AlterField(
            model_name='bpreading',
            name='recorded_at',
            field=models.DateTimeField(),
        ),
        migrations.RunPython(set_default_recorded_at),
    ]
