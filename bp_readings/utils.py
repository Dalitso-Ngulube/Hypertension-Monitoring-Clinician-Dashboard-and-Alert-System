def classify_bp(systolic, diastolic):
    if systolic >= 180 or diastolic >= 120:
        return "CRISIS"
    elif systolic >= 140 or diastolic >= 90:
        return "STAGE_2"
    elif systolic >= 130 or diastolic >= 80:
        return "STAGE_1"
    elif systolic >= 120:
        return "ELEVATED"
    return "NORMAL"