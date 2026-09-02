from rest_framework import serializers


class BPTrendSerializer(serializers.Serializer):
    date = serializers.DateField()
    avg_systolic = serializers.FloatField()
    avg_diastolic = serializers.FloatField()
    count = serializers.IntegerField()