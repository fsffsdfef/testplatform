from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from commons.cusntom.view import CustomResponse
from ..sers.interface_case_ser import *


class HttpCaseView(ModelViewSet):
    permission_classes = []
    queryset = HttpCaseModel.objects.all()
    serializer_class = HttpCaseSer


class ExpressItemView(ModelViewSet):
    permission_classes = []
    queryset = ExpressItem.objects.all()
    serializer_class = ExpressItemSer


class ExpressView(ModelViewSet):
    permission_classes = []
    queryset = Expresses.objects.all()
    serializer_class = ExpressSer


class OperatorByExpressView(APIView):
    permission_classes = []
    _OperatorMAP = {
        "==": "等于",
        ">": "大于",
        "<": "小于",
        ">=": "大于等于",
        "<=": "小于等于",
        "+": "加",
        "!=null": "不为空",
        "null": "为空",
        "re": "正则匹配",
        "like": "模糊匹配",
        "in": "包含于"
    }

    def get(self, request):
        return CustomResponse(data=self._OperatorMAP)


operView = OperatorByExpressView().as_view()