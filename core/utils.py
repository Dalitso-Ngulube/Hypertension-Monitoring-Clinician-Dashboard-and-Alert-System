def classify_bp(systolic, diastolic):
    if systolic >= 180 or diastolic >= 120:
        return "CRISIS"
    if systolic >= 140 or diastolic >= 90:
        return "STAGE_2"
    if systolic >= 130 or diastolic >= 80:
        return "STAGE_1"
    if systolic >= 120:
        return "ELEVATED"
    return "NORMAL"

CLASSIFY_BP_CHOICES = [
    ("CRISIS", "Crisis"),
    ("STAGE_2", "Stage 2"),
    ("STAGE_1", "Stage 1"),
    ("ELEVATED", "Elevated"),
    ("NORMAL", "Normal"),
]
