from rest_framework.generics import GenericAPIView
from django.db.models import Q
from ..sers.interface_case_ser import *
from commons.cusntom.view import CustomView
from commons.cusntom.pagination import CustomPage


class InterfaceView(GenericAPIView):

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
        }
    }


httpcase_view = InterfaceView.as_view()
