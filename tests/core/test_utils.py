import pytest
from core.utils import CLASSIFY_BP_CHOICES, classify_bp

@pytest.mark.parametrize("systolic, diastolic, expected", [
    (119, 79, "NORMAL"),
    (120, 79, "ELEVATED"),
    (125, 75, "ELEVATED"),
    (129, 79, "ELEVATED"),
    (130, 80, "STAGE_1"),
    (139, 89, "STAGE_1"),
    (140, 90, "STAGE_2"),
    (160, 100, "STAGE_2"),
    (180, 119, "STAGE_2"),
    (181, 100, "CRISIS"),
    (160, 121, "CRISIS"),
])
def test_classify_bp(systolic, diastolic, expected):
    assert classify_bp(systolic, diastolic) == expected

def test_choices_exist():
    assert len(CLASSIFY_BP_CHOICES) == 5
    choices = [c[0] for c in CLASSIFY_BP_CHOICES]
    assert set(choices) == {"CRISIS", "STAGE_2", "STAGE_1", "ELEVATED", "NORMAL"}