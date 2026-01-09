from rest_framework import serializers
from django_celery_beat.models import (
    PeriodicTask,
    PeriodicTasks,
    IntervalSchedule,
    ClockedSchedule,
    SolarSchedule,
    CrontabSchedule
)


class PeriodcTaskSer(serializers.ModelSerializer):

    class Meta:
        model = PeriodicTask
        fields = '__all__'

    def validate(self, attr):
        print(attr)
        return attr


class PeriodicTasksSer(serializers.ModelSerializer):

    class Meta:
        model = PeriodicTasks
        fields = '__all__'


class IntervalScheduleSer(serializers.ModelSerializer):

    class Meta:
        model = IntervalSchedule
        fields = '__all__'


class ClockedScheduleSer(serializers.ModelSerializer):

    class Meta:
        model = ClockedSchedule
        fields = '__all__'


class SolarScheduleSer(serializers.ModelSerializer):

    class Meta:
        model = SolarSchedule
        fields = '__all__'


class CrontabScheduleSer(serializers.ModelSerializer):

    class Meta:
        model = CrontabSchedule
        fields = '__all__'
