import pytest

from alerts.models import Alert
from analytics import evaluation
from bp_readings.models import BPReading
from core.management.commands.evaluate import Command
from tests.factories import AlertFactory, BPReadingFactory, PatientFactory

pytestmark = pytest.mark.django_db


def test_reference_classifier_covers_all_thresholds():
    assert evaluation._reference_classify(181, 80) == 'CRISIS'
    assert evaluation._reference_classify(120, 121) == 'CRISIS'
    assert evaluation._reference_classify(140, 80) == 'STAGE_2'
    assert evaluation._reference_classify(130, 80) == 'STAGE_1'
    assert evaluation._reference_classify(120, 70) == 'ELEVATED'
    assert evaluation._reference_classify(119, 79) == 'NORMAL'


def test_reference_set_has_50_distinct_cases():
    rows = evaluation._reference_readings()
    assert len(rows) == 50
    distinct_pairs = {(row['systolic'], row['diastolic']) for row in rows}
    assert len(distinct_pairs) == 50

    counts = {category: 0 for category in evaluation.RISK_CATEGORIES}
    for row in rows:
        counts[row['expected']] += 1

    assert counts == {category: 10 for category in evaluation.RISK_CATEGORIES}


def test_reference_data_accuracy_report(monkeypatch):
    monkeypatch.setattr(evaluation, '_reference_readings', lambda: [
        {'id': '1', 'systolic': 120, 'diastolic': 70, 'expected': 'ELEVATED'},
        {'id': '2', 'systolic': 119, 'diastolic': 79, 'expected': 'NORMAL'},
    ])

    report = evaluation.evaluate_classification_accuracy()

    assert report['accuracy'] == 100
    assert report['total'] == 2
    assert report['correct'] == 2
    assert report['per_category']['ELEVATED']['sensitivity'] == 100


def test_empty_reference_data_returns_zero_report(monkeypatch):
    monkeypatch.setattr(evaluation, '_reference_readings', lambda: [])

    assert evaluation.evaluate_classification_accuracy() == {
        'accuracy': 0,
        'total': 0,
        'correct': 0,
        'message': 'No readings found',
    }


def test_reference_reader_parses_csv(monkeypatch, tmp_path):
    reference_file = tmp_path / 'reference.csv'
    reference_file.write_text(
        'id,systolic,diastolic,expected_category\n1,120,70,ELEVATED\n',
        encoding='ascii',
    )
    monkeypatch.setattr(evaluation, 'REFERENCE_SET', reference_file)

    assert evaluation._reference_readings() == [{
        'id': '1',
        'systolic': 120,
        'diastolic': 70,
        'expected': 'ELEVATED',
    }]


def test_alert_sensitivity_and_report_aggregates():
    patient = PatientFactory()
    crisis = BPReadingFactory(patient=patient, systolic=190, diastolic=125)
    BPReadingFactory(patient=patient, systolic=120, diastolic=70)
    AlertFactory(patient=patient, reading=crisis, alert_type='CRISIS')

    metrics = evaluation.evaluate_alert_sensitivity()
    report = evaluation.generate_evaluation_report()

    assert metrics['sensitivity'] == 100
    assert metrics['specificity'] == 100
    assert report['total_patients'] == 2  # PatientFactory creates a linked user profile.
    assert report['total_readings'] == 2
    assert report['total_alerts'] == Alert.objects.count()
    assert sum(row['count'] for row in report['readings_by_risk']) == 2


def test_alert_metrics_without_crisis_readings():
    patient = PatientFactory()
    BPReadingFactory(patient=patient, systolic=120, diastolic=70)

    metrics = evaluation.evaluate_alert_sensitivity()

    assert metrics['sensitivity'] is None
    assert metrics['sensitivity_status'] == 'not_evaluable_no_crisis_readings'


def test_print_evaluation_report_formats_summary(capsys, monkeypatch):
    report = {
        'classification_accuracy': {'accuracy': 100, 'total': 2, 'correct': 2},
        'alert_performance': {
            'sensitivity': None,
            'specificity': 100,
            'total_crisis_readings': 0,
            'alerted_crisis_readings': 0,
            'missed_alerts': 0,
        },
        'total_patients': 0,
        'total_readings': 0,
        'total_alerts': 0,
        'readings_by_risk': [{'risk_category': 'NORMAL', 'count': 0}],
        'alerts_by_severity': [{'severity': 'LOW', 'count': 0}],
    }
    monkeypatch.setattr(evaluation, 'generate_evaluation_report', lambda: report)

    evaluation.print_evaluation_report()

    output = capsys.readouterr().out
    assert 'Not evaluable (no crisis readings)' in output
    assert 'NORMAL: 0' in output
    assert 'LOW: 0' in output


def test_evaluation_command_json_and_save_modes(tmp_path, monkeypatch):
    from io import StringIO

    report = {'summary': 'test report'}
    monkeypatch.setattr(
        'core.management.commands.evaluate.generate_evaluation_report',
        lambda: report,
    )
    monkeypatch.chdir(tmp_path)
    command = Command()
    command.stdout = StringIO()

    command.handle(json=True, save=False)
    assert 'test report' in command.stdout.getvalue()

    command.stdout = StringIO()
    command.handle(json=False, save=True)
    saved = list(tmp_path.glob('evaluation_report_*.json'))
    assert len(saved) == 1
    assert saved[0].read_text(encoding='utf-8')
    assert 'Report saved to' in command.stdout.getvalue()