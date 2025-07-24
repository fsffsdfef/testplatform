from commons.cusntom.view import CustomView
from commons.cusntom.response import CustomResponse
from commons.utils.request import AutomatedRequest
from apps.automatic.sers import SuitSer
from apps.automatic.models import SuitModel


# Create your views here.


class TestView(CustomView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        suit_id = request.data.get('suitId')
        suit_obj = SuitModel.objects.get(suitId=suit_id)
        suit_ser = SuitSer(instance=suit_obj)
        data = suit_ser.data['caseInfo']
        answer = list()
        for case in data:
            a = AutomatedRequest(case).http_send()
            answer.append(a)
        return CustomResponse(data=answer, msg="o", code=101)
