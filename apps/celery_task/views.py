from apps.automatic.sers import SuitSer
from apps.automatic.models import SuitModel
from apps.cases.model.interface_case import HttpCaseModel
from apps.cases.sers import interface_case_ser
from commons.cusntom.pagination import CustomPage
from commons.utils.getcasedata import GetCaseData
from commons.cusntom.view import CustomView
from commons.cusntom.response import CustomResponse
from commons.factory.requestFactory import RequestDispense
from rest_framework.viewsets import ModelViewSet
from .sers import (
    PeriodcTaskSer, PeriodicTasksSer,
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

# Create your views here.


class TestView(CustomView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        suit_id = request.data.get('suitId', None)
        case_id = request.data.get('caseId', None)
        if suit_id:
            return self.suit_action(suit_id)
        elif case_id:
            return self.https_action(case_id)
        else:
            return CustomResponse(data=[], code=101, msg="暂不支持")

    @staticmethod
    def suit_action(data):
        client = RequestDispense()
        # logger.info("日志测试", extra={'request': request.data})
        suit_obj = SuitModel.objects.get(suitId=data)
        suit_ser = SuitSer(instance=suit_obj)
        data = suit_ser.data['caseInfo']
        suit_id = suit_ser.data['suitId']
        suit_name = suit_ser.data['suitName']
        try:
            answer = client.http_request(data)
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
            answer = client.http_request(data=info)
            return CustomResponse(data=answer, code=100)
        except Exception as e:
            return CustomResponse(data=[], code=102, msg=str(e))

    def dubbo_action(self, data):
        pass

    def ui_action(self, data):
        pass


# class PeriodcTaskView(CustomView):
#     model = PeriodicTask
#     serializer_class = PeriodcTaskSer
#     permission_classes = []
#
#     authentication_classes = []
#     pagination_class = CustomPage
#
#     fields = {
#         "id": {
#             "type": 'exact',
#             "converter": int,
#             "allow_empty": False
#         },
#         "name": {
#             "type": 'icontains',
#             "converter": str,
#             "allow_empty": True
#         }
#     }
#     index_key = "id"
#
#
# task_view = PeriodcTaskView.as_view()
class PeriodcTaskView(ModelViewSet):
    queryset = PeriodicTask.objects.all()
    serializer_class = PeriodcTaskSer
    permission_classes = []


class PeriodcTasksView(ModelViewSet):

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
