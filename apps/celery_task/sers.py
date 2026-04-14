from rest_framework import serializers
from django_celery_beat.models import (
    PeriodicTask,
    PeriodicTasks,
    IntervalSchedule,
    ClockedSchedule,
    SolarSchedule,
    CrontabSchedule
)


class PeriodicTaskSer(serializers.ModelSerializer):
    schedule = serializers.SerializerMethodField(method_name="_get_schedule")

    class Meta:
        model = PeriodicTask
        fields = '__all__'

    @staticmethod
    def _get_schedule(obj):
        if obj.interval:
            return obj.interval.__str__()
        elif obj.crontab:
            return obj.crontab.__str__()
        elif obj.clocked:
            return obj.clocked.__str__()
        return ''


class PeriodicTasksSer(serializers.ModelSerializer):

    class Meta:
        model = PeriodicTasks
        fields = '__all__'


class IntervalScheduleSer(serializers.ModelSerializer):
    intervalName = serializers.SerializerMethodField(method_name="_get_interval_name")

    class Meta:
        model = IntervalSchedule
        fields = '__all__'

    @staticmethod
    def _get_interval_name(obj):
        return f"{str(obj.every)} {obj.period}"


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
        # fields = '__all__'
        exclude = ["timezone"]
