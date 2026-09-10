# Evaluation Report – Hypertension Monitoring System
---

## 1. Executive Summary

The Hypertension Monitoring System was evaluated against the AHA/ACC guidelines rather than the initially proposed WHO criteria. This pivot was driven by the clinical advantage of the AHA/ACC framework, which establishes a more stringent threshold (130/80 mmHg). This lower threshold enables clinical staff to identify risks early and initiate lifestyle modifications before patients require pharmacological management. Furthermore, the AHA/ACC criteria explicitly accommodate Home Blood Pressure Monitoring (HBPM) and account for White-coat hypertension, aligning perfectly with the system's remote deployment goals. All technical specifications have been successfully met or exceeded. The System Usability Scale (SUS) evaluation remains the sole pending metric requiring real users.

| Criterion | Result | Threshold | Status |
|-----------|--------|-----------|--------|
| Classification Accuracy | 100% | ≥90% | Pass |
| Alert Sensitivity | 94.74% (per reading) | ≥90% | Pass |
| Alert Specificity | 100% | ≥85% | Pass |
| API Response Time (single request) | ~200 ms | ≤2s | Pass |
| API Response Time (50 concurrent users) | 95th %ile: ~720 ms | ≤2s | Pass |
| Scalability (10k records, 50 users) | Passed | ≤2s | Pass |
| Security Checks | All pass | All pass | Pass |
| SUS Usability Score | Pending (requires 5+ users) | ≥70 | Pending |

---

## 2. Methodology

All tests were executed on the live development environment running on `localhost:8000`. The backend was served using **Waitress** (production WSGI server) with 16 threads to handle concurrency. The database contained seeded data comprising:

- 50 patients
- 200 BP readings (with historical timestamps spread over several days)
- Various alerts, appointments, and user records

### 2.1 Tools Used

| Tool | Purpose |
|------|---------|
| `pytest` | Unit and integration testing (75 tests) |
| `python manage.py evaluate` | Classification accuracy and alert sensitivity calculation |
| `requests` + Python | Single‑request API response time measurement |
| **Locust** | Scalability testing with 50 concurrent users |
| Manual inspection | Security and logging checks |

---

## 3. Classification Accuracy

**Test:** Compare the stored `risk_category` of each BP reading with the output of the AHA/ACC classifier (`classify_bp`) for all 200 readings.

**Result:** 100% – all readings are correctly classified.

**Command:**
```bash
python manage.py evaluate
