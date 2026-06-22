import pytest
from core.utils import classify_bp, CLASSIFY_BP_CHOICES

@pytest.mark.unit
class TestBPClassification:
    @pytest.mark.parametrize("systolic,diastolic,expected", [
        (180, 100, "CRISIS"),
        (150, 120, "CRISIS"),
        (145, 95, "STAGE_2"),
        (135, 85, "STAGE_1"),
        (125, 75, "ELEVATED"),
        (118, 78, "NORMAL"),
        (90, 60, "NORMAL"),
    ])
    def test_classify(self, systolic, diastolic, expected):
        assert classify_bp(systolic, diastolic) == expected

    def test_choices_exist(self):
        assert len(CLASSIFY_BP_CHOICES) == 5
        choices = [choice[0] for choice in CLASSIFY_BP_CHOICES]
        assert "CRISIS" in choices