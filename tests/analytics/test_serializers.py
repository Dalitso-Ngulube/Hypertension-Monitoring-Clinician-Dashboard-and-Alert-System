from datetime import date

import pytest

from analytics.serializers import BPTrendSerializer


@pytest.mark.parametrize('payload', [
    {
        'date': date(2026, 1, 1),
        'avg_systolic': 120.5,
        'avg_diastolic': 80.5,
        'count': 3,
    },
    {
        'date': '2026-01-01',
        'avg_systolic': 120,
        'avg_diastolic': 80,
        'count': 3,
    },
])
def test_bp_trend_serializer_accepts_valid_payload(payload):
    serializer = BPTrendSerializer(data=payload)

    assert serializer.is_valid(), serializer.errors


def test_bp_trend_serializer_rejects_invalid_payload():
    serializer = BPTrendSerializer(data={
        'date': 'not-a-date',
        'avg_systolic': 'high',
        'avg_diastolic': 80,
        'count': 'many',
    })

    assert not serializer.is_valid()
    assert set(serializer.errors) == {'date', 'avg_systolic', 'count'}