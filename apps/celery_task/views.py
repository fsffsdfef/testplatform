from apps.automatic.sers import SuitSer
from apps.automatic.models import SuitModel
from apps.cases.model.interface_case import HttpCaseModel
from celery import current_app
from commons.cusntom.pagination import CustomPage
from commons.utils.get_case_data import GetCaseData
from commons.cusntom.view import CustomView
from commons.cusntom.response import CustomResponse
from commons.factory.requestFactory import RequestDispense
from commons.utils.read_file import Read
from rest_framework.viewsets import ModelViewSet
import logging
from .sers import (
    PeriodicTaskSer, PeriodicTasksSer,
    ClockedScheduleSer, CrontabScheduleSer,
    IntervalScheduleSer, SolarScheduleSer
)
from django_celery_beat.models import (
    PeriodicTask,
    PeriodicTasks,
    IntervalSchedule,
    ClockedSchedule,
    SolarSchedule,
    CrontabSchedule
)


logger = logging.getLogger(__name__)
#
# # Create your views here.


class TestView(CustomView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        suit_id = request.data.get('suitId', None)
        case_id = request.data.get('caseId', None)
        if suit_id:
            logger.info(f"{request.data['suitName']}套件执行", extra={'req': request.data})
            return self.suit_action(suit_id)
        elif case_id:
            logger.info(f"{request.data['portName']}接口{request.data['caseName']}用例执行", extra={'req': request.data})
            return self.https_action(case_id)
        else:
            return CustomResponse(data=[], code=101, msg="暂不支持")

    @staticmethod
    def suit_action(data):
        client = RequestDispense()
        suit_obj = SuitModel.objects.get(suitId=data)
        suit_ser = SuitSer(instance=suit_obj)
        data = suit_ser.data['caseInfo']
        suit_id = suit_ser.data['suitId']
        suit_name = suit_ser.data['suitName']
        try:
            answer = client.send_request(request_type="HTTP", data=data)
            answer['suitID'] = suit_id
            answer['suitName'] = suit_name
            return CustomResponse(data=answer, code=101)
        except Exception as e:
            return CustomResponse(data=[], code=101, msg=str(e))

    @staticmethod
    def https_action(data):
        client = RequestDispense()
        try:
            case = HttpCaseModel.objects.get(caseId=data)
            info = GetCaseData(case).get_case("onecase")
            answer = client.send_request(request_type="HTTP", data=info)
            logger.info(f"{case}用例返回", extra={'res': answer})
            return CustomResponse(data=answer, code=100)
        except Exception as e:
            logger.info(f"{data}用例返回", extra={'res': str(e)})
            return CustomResponse(data=[], code=102, msg=str(e))

    def dubbo_action(self, data):
        pass

    def ui_action(self, data):
        pass


class GetTasks(CustomView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        task_list = Read(env="dev", filename="Tasks.json").get_json_file()["tasksMap"]
        return CustomResponse(data={"list": task_list}, code=101)


get_tasks = GetTasks.as_view()


class CustomPeriodicTaskView(CustomView):
    model = PeriodicTask
    serializer_class = PeriodicTaskSer
    permission_classes = []
    pagination_class = CustomPage
    fields = {
        "id": {
            "type": 'exact',
            "converter": int,
            "allow_empty": False
        },
        "name": {
            "type": 'icontains',
            "converter": str,
            "allow_empty": True
        }
    }
    index_key = "id"


class CustomIntervalScheduleView(CustomView):
    model = IntervalSchedule
    serializer_class = IntervalScheduleSer
    permission_classes = []
    pagination_class = CustomPage
    fields = {
        "id": {
            "type": 'exact',
            "converter": int,
            "allow_empty": False
        }
    }
    index_key = "id"


interval_view = CustomIntervalScheduleView.as_view()
task_view = CustomPeriodicTaskView.as_view()


class PeriodicTaskView(ModelViewSet):
    queryset = PeriodicTask.objects.all()
    serializer_class = PeriodicTaskSer
    permission_classes = []


class PeriodicTasksView(ModelViewSet):

    queryset = PeriodicTasks.objects.all()
    serializer_class = PeriodicTasksSer
    permission_classes = []


class IntervalScheduleView(ModelViewSet):

    queryset = IntervalSchedule.objects.all()
    serializer_class = IntervalScheduleSer
    permission_classes = []


class ClockedScheduleView(ModelViewSet):

    queryset = ClockedSchedule.objects.all()
    serializer_class = ClockedScheduleSer
    permission_classes = []


class SolarScheduleView(ModelViewSet):

    queryset = SolarSchedule.objects.all()
    serializer_class = SolarScheduleSer
    permission_classes = []


class CrontabScheduleView(ModelViewSet):

    queryset = CrontabSchedule.objects.all()
    serializer_class = CrontabScheduleSer
    permission_classes = []
