# Evaluation Report: Hypertension Monitoring System

Run date: 15 September 2026

## 1. Reference-set classification results

Reference file: `analytics/reference_readings.csv` (50 readings, ten per
category). Each row cites the AHA/ACC 2017 guideline BP categories table in
the `source` column. This is a standards-based reference set, not
clinician-confirmed patient data.

Overall accuracy: **100.00%** (`50/50`) | Status: **PASS** against the
reference labels.

### Confusion matrix

Rows are expected categories; columns are predicted categories.

| Expected \ Predicted | NORMAL | ELEVATED | STAGE_1 | STAGE_2 | CRISIS |
|---|---:|---:|---:|---:|---:|
| NORMAL   | 10 | 0 | 0 | 0 | 0 |
| ELEVATED | 0 | 10 | 0 | 0 | 0 |
| STAGE_1  | 0 | 0 | 10 | 0 | 0 |
| STAGE_2  | 0 | 0 | 0 | 10 | 0 |
| CRISIS   | 0 | 0 | 0 | 0 | 10 |

### Per-category metrics

| Category | TP | FN | FP | TN | Sensitivity | Specificity |
|---|---:|---:|---:|---:|---:|---:|
| NORMAL   | 10 | 0 | 0 | 40 | 100.00% | 100.00% |
| ELEVATED | 10 | 0 | 0 | 40 | 100.00% | 100.00% |
| STAGE_1  | 10 | 0 | 0 | 40 | 100.00% | 100.00% |
| STAGE_2  | 10 | 0 | 0 | 40 | 100.00% | 100.00% |
| CRISIS   | 10 | 0 | 0 | 40 | 100.00% | 100.00% |

The implementation classified every cited boundary, systolic-only,
diastolic-only, and mixed case as expected. These results establish agreement
with the independently coded reference table; they do not establish clinical
validity or replace clinician review.

The production classifier used by `BPReading.save()` and the independent
reference classifier used by `analytics/evaluation.py` are currently identical
implementations of the AHA/ACC threshold table. The reference classifier is
still kept separate in the evaluation path so that any future divergence is
detected rather than hidden by comparing a model value with the same function
that produced it.

## 2. Reference-set provenance

The `source` value on every row is `AHA/ACC 2017 Guideline BP categories
table`. The expected labels follow the 2017 ACC/AHA thresholds: normal,
elevated, stage 1, stage 2, and crisis. A clinician sign-off is still required
before describing this file as clinically labelled. Reviewer name and date:
**pending**.

## 3. Alert evaluation

Crisis alerts are keyed by the `Alert.reading` foreign key and alert type, so
repeated crisis readings for one patient are evaluated individually. The
report counts true positives, missed crisis alerts, false crisis alerts, and
true negatives per reading.

The 15 September 2026 evaluation database contains 500 readings, including 56
crisis and 444 non-crisis readings. Crisis sensitivity and specificity are
therefore measurable.

| Metric | Result | Counts | Status |
|---|---:|---|---|
| Sensitivity | 100.00% | TP 56, FN 0; crisis readings 56 | PASS |
| Specificity | 100.00% | FP 0, TN 444; non-crisis readings 444 | PASS |

Run command:

```bash
python manage.py evaluate --json
