from django.shortcuts import render
from utils.customview import CustomView
from utils.baseresponse import BaseResponse
from rest_framework.views import APIView
from apps.celery_task.sers import *
from django_celery_beat.models import *
from celerys.tasks import interface_automation_task
from celery.result import AsyncResult
from celery import result
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


class Demo(APIView):
    permission_classes = []
    def post(self, request):
        task_type = request.data.get('task_type', 'apply_case')
        id = request.data.get('applyId', None)
        if id is None:
            return BaseResponse(data={'msg': 'id不能为空'})
        re = interface_automation_task.delay(id=id, task_type=task_type)
        ar = result.AsyncResult(re.id)  # 获取执行结果
        if ar.ready():  # 是否执行完成
            return BaseResponse(data={'status': ar.state, 'result': ar.get()})
        return BaseResponse(data={'id': re.id, 'status': ar.state, 'res': ar.get()})


class Demo1(APIView):
    permission_classes = []
    def get(self, request):
        return BaseResponse(data={'id': '123323'})




