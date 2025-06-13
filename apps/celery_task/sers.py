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
