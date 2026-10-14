# Evaluation Report: Hypertension Monitoring System

Run date: 14th October 2026
Commit: 3b4a7819016a407ae098ce4430f1c8bf96afd29a

## 1. Reference-set classification results

Reference file: `analytics/reference_readings.csv` (50 distinct readings,
ten per category). Each row cites the AHA/ACC 2017 guideline BP categories
table in the `source` column. This is a standards-based reference set, not
clinician-confirmed patient data.

A regression test (`test_reference_set_has_50_distinct_cases`) asserts
that the file contains exactly 50 distinct (systolic, diastolic) pairs
with ten in each AHA/ACC category, so future edits cannot silently reduce
the set.

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
diastolic-only, and mixed case as expected.

### What the accuracy figure does and does not show

The production classifier (invoked by `BPReading.save()`) and the
reference classifier (used by `analytics/evaluation.py`) are two separate
implementations of the same AHA/ACC threshold table. They agree by
construction on the current reference set, so the 100% figure
demonstrates internal consistency between the two code paths, not
independent verification of the AHA/ACC table itself.

The value of the two-implementation design is prospective: if either the
production or the reference classifier is changed — for example, when the
WHO 2021 treatment thresholds are integrated in future work — the two
will diverge, and the evaluation harness will flag the divergence instead
of silently absorbing it. This is why the reference classifier is kept
in a separate module rather than sharing code with the production
classifier.

The 100% figure should therefore be read as a regression guard against
accidental classifier change, not as evidence of clinical accuracy.
Clinical accuracy would require a clinician-labelled reference set (see
section 2).

## 2. Reference-set provenance

The `source` value on every row is `AHA/ACC 2017 Guideline BP categories
table`. The expected labels follow the 2017 ACC/AHA thresholds: normal,
elevated, stage 1, stage 2, and crisis. A clinician sign-off is still
required before describing this file as clinically labelled. Reviewer
name and date: **pending**.

## 3. Alert evaluation

Crisis alerts are keyed by the `Alert.reading` foreign key and alert type,
so repeated crisis readings for one patient are evaluated individually.
The report counts true positives, missed crisis alerts, false crisis
alerts, and true negatives per reading.

| Metric | Result | Counts | Status |
|---|---:|---|---|
| Sensitivity | 100.00% | TP 987, FN 0; crisis readings 987 | PASS |
| Specificity | 100.00% | FP 0, TN 9,013; non-crisis readings 9,013 | PASS |
