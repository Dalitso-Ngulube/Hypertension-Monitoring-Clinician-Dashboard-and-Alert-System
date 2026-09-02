
from django.db.models import Count
from django.utils import timezone

from alerts.models import Alert
from bp_readings.models import BPReading
from core.utils import classify_bp
from patients.models import Patient


def evaluate_classification_accuracy():
    readings = BPReading.objects.all()
    total = readings.count()

    if total == 0:
        return {
            'accuracy': 0,
            'total': 0,
            'correct': 0,
            'message': 'No readings found'
        }

    correct = 0
    confusion = {}

    for reading in readings:
        expected = classify_bp(reading.systolic, reading.diastolic)
        actual = reading.risk_category

        if expected == actual:
            correct += 1

        key = f"{expected}->{actual}"
        confusion[key] = confusion.get(key, 0) + 1

    return {
        'accuracy': round((correct / total) * 100, 2),
        'total': total,
        'correct': correct,
        'confusion_matrix': confusion
    }


def evaluate_alert_sensitivity():
    crisis_readings = BPReading.objects.filter(risk_category='CRISIS')
    total_crisis_readings = crisis_readings.count()

    crisis_alerts = Alert.objects.filter(alert_type='CRISIS')
    total_crisis_alerts = crisis_alerts.count()

    patients_with_crisis = crisis_readings.values('patient').distinct().count()
    patients_with_alert = crisis_alerts.values('patient').distinct().count()

    return {
        'sensitivity_per_reading': round((total_crisis_alerts / total_crisis_readings) * 100, 2) if total_crisis_readings else 0,
        'sensitivity_per_patient': round((patients_with_alert / patients_with_crisis) * 100, 2) if patients_with_crisis else 0,
        'total_crisis_readings': total_crisis_readings,
        'total_crisis_alerts': total_crisis_alerts,
        'patients_with_crisis': patients_with_crisis,
        'patients_with_alert': patients_with_alert,
        'missed_alerts': total_crisis_readings - total_crisis_alerts
    }


def generate_evaluation_report():
    classification = evaluate_classification_accuracy()
    alerts = evaluate_alert_sensitivity()

    return {
        'timestamp': str(timezone.now()),
        'classification_accuracy': classification,
        'alert_performance': alerts,
        'total_patients': Patient.objects.count(),
        'total_readings': BPReading.objects.count(),
        'total_alerts': Alert.objects.count(),
        'alerts_by_severity': list(Alert.objects.values('severity').annotate(count=Count('id'))),
        'readings_by_risk': list(BPReading.objects.values('risk_category').annotate(count=Count('id')))
    }


def print_evaluation_report():
    report = generate_evaluation_report()
    print("\n" + "="*60)
    print("EVALUATION REPORT - Hypertension Monitoring System")
    print("="*60)
    print(f"\n[Classification Accuracy (AHA/ACC)]: {report['classification_accuracy']['accuracy']}%")
    print(f"   Total Readings: {report['classification_accuracy']['total']}")
    print(f"   Correctly Classified: {report['classification_accuracy']['correct']}")

    print("\n[Alert Sensitivity]:")
    print(f"   Per Reading: {report['alert_performance']['sensitivity_per_reading']}%")
    print(f"   Per Patient: {report['alert_performance']['sensitivity_per_patient']}%")
    print(f"   Total Crisis Readings: {report['alert_performance']['total_crisis_readings']}")
    print(f"   Crisis Alerts Generated: {report['alert_performance']['total_crisis_alerts']}")
    print(f"   Patients with Crisis: {report['alert_performance']['patients_with_crisis']}")
    print(f"   Patients with Alerts: {report['alert_performance']['patients_with_alert']}")
    print(f"   Missed Alerts: {report['alert_performance']['missed_alerts']}")

    print("\n[System Overview]:")
    print(f"   Total Patients: {report['total_patients']}")
    print(f"   Total Readings: {report['total_readings']}")
    print(f"   Total Alerts: {report['total_alerts']}")

    print("\n[Readings by Risk Category]:")
    for item in report['readings_by_risk']:
        print(f"   {item['risk_category']}: {item['count']}")

    print("\n[Alerts by Severity]:")
    for item in report['alerts_by_severity']:
        print(f"   {item['severity']}: {item['count']}")

    print("\n" + "="*60)
