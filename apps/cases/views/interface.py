from rest_framework.generics import GenericAPIView
from django.db.models import Q
from ..sers.interface_case_ser import *
from commons.cusntom.view import CustomView
from commons.cusntom.pagination import CustomPage
from commons.cusntom.response import CustomResponse


class InterfaceView(CustomView):

    model = HttpCaseModel
    serializer_class = HttpCaseSer
    permission_classes = []
    pagination_class = CustomPage
    fields = {
        "caseId": {
            "type": 'exact',
            "converter": int,
            "allow_empty": False
        },
        "caseName": {
            "type": 'icontains',
            "converter": str,
            "allow_empty": True
        },
        "portId": {
            "type": 'icontains',
            "converter": int,
            "allow_empty": True,
            'related_field': 'port__portId',
            'related_lookup_type': 'icontains'
        },
        "portName": {
            "type": 'icontains',
            "converter": str,
            "allow_empty": True,
            'related_field': 'port__portName',
            'related_lookup_type': 'icontains'
        }
    }
    index_key = "caseId"

    def delete(self, request, *args, **kwargs):
        case_id = request.get('caseId')
        obj = self.model.objects.get(caseId=case_id)
        suit_rel = obj.suit.all().values('suitName', 'suitId')
        suit_list = list()
        if suit_rel is not None:
            for suit in suit_rel:
                suit_list.append(suit['suitName'])
        if len(suit_list) > 0:
            return CustomResponse(data=[], msg=f"{suit_list}套件正在使用，不可删除", code=101, success=False)
        else:
            return super().delete(request, *args, **kwargs)


httpcase_view = InterfaceView.as_view()
