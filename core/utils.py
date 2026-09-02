"""
Blood pressure classification using AHA/ACC 2017 guidelines (reaffirmed 2025).
This single classification applies to office, home, and ABPM readings.

Stages (mmHg):
    - NORMAL:          SBP < 120   and  DBP < 80
    - ELEVATED:        SBP 120-129  and  DBP < 80   (only systolic elevation)
    - STAGE_1:         SBP 130-139  or   DBP 80-89
    - STAGE_2:         SBP >= 140   or   DBP >= 90
    - CRISIS:          SBP > 180    or   DBP > 120  (emergency threshold)

Note: If systolic and diastolic fall in different categories,
the higher category applies (handled by `or` conditions).
"""

def classify_bp(systolic: int, diastolic: int) -> str:
    if systolic > 180 or diastolic > 120:
        return "CRISIS"
    if systolic >= 140 or diastolic >= 90:
        return "STAGE_2"
    if systolic >= 130 or diastolic >= 80:
        return "STAGE_1"
    if systolic >= 120 and diastolic < 80:
        return "ELEVATED"
    return "NORMAL"


# ---------------------------------------------------------------------------
# WHO 2021 treatment‑flag 
# ---------------------------------------------------------------------------

def who_treatment_flag(systolic: int, diastolic: int, high_cv_risk: bool = False) -> bool:
    """
    True if WHO 2021 recommends considering treatment:
      - BP >= 140/90, OR
      - BP >= 130 systolic + high CV risk
    """
    if systolic >= 140 or diastolic >= 90:
        return True
    if high_cv_risk and systolic >= 130:
        return True
    return False


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CLASSIFY_BP_CHOICES = [
    ("CRISIS", "Crisis"),
    ("STAGE_2", "Stage 2"),
    ("STAGE_1", "Stage 1"),
    ("ELEVATED", "Elevated"),
    ("NORMAL", "Normal"),
]

RISK_COLORS = {
    "CRISIS": "danger",
    "STAGE_2": "danger",
    "STAGE_1": "warning",
    "ELEVATED": "info",
    "NORMAL": "success",
}

RISK_SEVERITY = {
    "CRISIS": "CRITICAL",
    "STAGE_2": "HIGH",
    "STAGE_1": "MEDIUM",
    "ELEVATED": "LOW",
    "NORMAL": "LOW",
}

RISK_DESCRIPTIONS = {
    "CRISIS": "Hypertensive crisis — immediate medical attention required",
    "STAGE_2": "Stage 2 hypertension — treatment recommended",
    "STAGE_1": "Stage 1 hypertension — lifestyle modification and monitoring",
    "ELEVATED": "Elevated blood pressure — lifestyle modification recommended",
    "NORMAL": "Normal blood pressure — continue monitoring",
}
