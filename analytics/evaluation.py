
import csv
from pathlib import Path

from django.db.models import Count
from django.utils import timezone

from alerts.models import Alert
from bp_readings.models import BPReading
from core.utils import classify_bp
from patients.models import Patient

REFERENCE_SET = Path(__file__).with_name('reference_readings.csv')
RISK_CATEGORIES = ('NORMAL', 'ELEVATED', 'STAGE_1', 'STAGE_2', 'CRISIS')


def _reference_classify(systolic, diastolic):
    if systolic > 180 or diastolic > 120:
        return 'CRISIS'
    if systolic >= 140 or diastolic >= 90:
        return 'STAGE_2'
    if systolic >= 130 or diastolic >= 80:
        return 'STAGE_1'
    if systolic >= 120 and diastolic < 80:
        return 'ELEVATED'
    return 'NORMAL'


def _reference_readings():
    with REFERENCE_SET.open(newline='', encoding='ascii') as reference_file:
        return [
            {
                'id': row['id'],
                'systolic': int(row['systolic']),
                'diastolic': int(row['diastolic']),
                'expected': row['expected_category'],
            }
            for row in csv.DictReader(reference_file)
        ]


def evaluate_classification_accuracy():
    readings = _reference_readings()
    total = len(readings)

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
        expected = reading['expected']
        actual = classify_bp(reading['systolic'], reading['diastolic'])

        if expected == actual:
            correct += 1

        key = f"{expected}->{actual}"
        confusion[key] = confusion.get(key, 0) + 1

    per_category = {}
    for category in RISK_CATEGORIES:
        true_positive = confusion.get(f'{category}->{category}', 0)
        false_negative = sum(
            count for key, count in confusion.items()
            if key.startswith(f'{category}->') and key != f'{category}->{category}'
        )
        false_positive = sum(
            count for key, count in confusion.items()
            if key.endswith(f'->{category}') and key != f'{category}->{category}'
        )
        true_negative = total - true_positive - false_negative - false_positive
        per_category[category] = {
            'true_positive': true_positive,
            'false_negative': false_negative,
            'false_positive': false_positive,
            'true_negative': true_negative,
            'sensitivity': round(true_positive / (true_positive + false_negative) * 100, 2)
            if true_positive + false_negative else 0,
            'specificity': round(true_negative / (true_negative + false_positive) * 100, 2)
            if true_negative + false_positive else 0,
        }

    return {
        'accuracy': round((correct / total) * 100, 2),
        'total': total,
        'correct': correct,
        'confusion_matrix': confusion,
        'per_category': per_category,
        'reference_set': str(REFERENCE_SET),
    }


def evaluate_alert_sensitivity():
    readings = list(BPReading.objects.all())
    crisis_readings = [
        reading for reading in readings
        if _reference_classify(reading.systolic, reading.diastolic) == 'CRISIS'
    ]
    non_crisis_readings = [reading for reading in readings if reading not in crisis_readings]

    def has_alert(reading):
        return Alert.objects.filter(
            reading=reading,
            alert_type='CRISIS',
        ).exists()

    alerted_crisis = sum(has_alert(reading) for reading in crisis_readings)
    false_crisis_alerts = sum(has_alert(reading) for reading in non_crisis_readings)
    total_crisis_readings = len(crisis_readings)
    total_non_crisis_readings = len(non_crisis_readings)

    return {
        'sensitivity': round((alerted_crisis / total_crisis_readings) * 100, 2) if total_crisis_readings else None,
        'sensitivity_status': 'measured' if total_crisis_readings else 'not_evaluable_no_crisis_readings',
        'specificity': round((total_non_crisis_readings - false_crisis_alerts) / total_non_crisis_readings * 100, 2)
        if total_non_crisis_readings else 0,
        'true_positive': alerted_crisis,
        'false_negative': total_crisis_readings - alerted_crisis,
        'false_positive': false_crisis_alerts,
        'true_negative': total_non_crisis_readings - false_crisis_alerts,
        'total_crisis_readings': total_crisis_readings,
        'alerted_crisis_readings': alerted_crisis,
        'missed_alerts': total_crisis_readings - alerted_crisis,
        'total_non_crisis_readings': total_non_crisis_readings,
        'false_crisis_alerts': false_crisis_alerts,
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
    print(f"\n[Reference-set Classification Accuracy (AHA/ACC)]: {report['classification_accuracy']['accuracy']}%")
    print(f"   Total Readings: {report['classification_accuracy']['total']}")
    print(f"   Correctly Classified: {report['classification_accuracy']['correct']}")

    print("\n[Alert Performance]:")
    sensitivity = report['alert_performance']['sensitivity']
    sensitivity_display = f'{sensitivity}%' if sensitivity is not None else 'Not evaluable (no crisis readings)'
    print(f"   Sensitivity: {sensitivity_display}")
    print(f"   Specificity: {report['alert_performance']['specificity']}%")
    print(f"   Total Crisis Readings: {report['alert_performance']['total_crisis_readings']}")
    print(f"   Crisis Readings Alerted: {report['alert_performance']['alerted_crisis_readings']}")
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
