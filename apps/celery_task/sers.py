from django_celery_beat.models import *
from rest_framework import serializers


class PeriodicTaskSer(serializers.ModelSerializer):
    class Meta:
        model = PeriodicTask
        fields = '__all__'


class PeriodicTasksSer(serializers.ModelSerializer):
    class Meta:
        model = PeriodicTasks
        fields = '__all__'


class SolarScheduleSer(serializers.ModelSerializer):
    class Meta:
        model = SolarSchedule
        fields = '__all__'


class IntervalScheduleSer(serializers.ModelSerializer):
    class Meta:
        model = IntervalSchedule
        fields = '__all__'


class CrontabScheduleSer(serializers.ModelSerializer):
    class Meta:
        model = CrontabSchedule
        fields = '__all__'


class ClockedScheduleSer(serializers.ModelSerializer):
    class Meta:
        model = ClockedSchedule
        fields = '__all__'

