from django.shortcuts import render
from utils.customview import CustomView
from rest_framework.views import APIView
from apps.celery_task.sers import *
from django_celery_beat.models import *
# Create your views here.


class PeriodicTaskView(CustomView):
    queryset = PeriodicTask.objects.all()
    serializer_class = PeriodicTaskSer
    permission_classes = []


class PeriodicTasksView(CustomView):
    queryset = PeriodicTasks.objects.all()
    serializer_class = PeriodicTasksSer
    permission_classes = []


class SolarScheduleView(CustomView):
    queryset = SolarSchedule.objects.all()
    serializer_class = SolarScheduleSer
    permission_classes = []


class IntervalScheduleView(CustomView):
    queryset = IntervalSchedule.objects.all()
    serializer_class = IntervalScheduleSer
    permission_classes = []


class CrontabScheduleView(CustomView):
    queryset = CrontabSchedule.objects.all()
    serializer_class = CrontabScheduleSer
    permission_classes = []


class ClockedScheduleView(CustomView):
    queryset = ClockedSchedule.objects.all()
    serializer_class = ClockedScheduleSer
    permission_classes = []


# class Demo(APIView):
#     def post(self, request):




