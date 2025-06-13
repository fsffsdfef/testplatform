from rest_framework.generics import GenericAPIView
from django.db.models import Q
from ..sers.depart_apply_port import *
from commons.cusntom.view import CustomView
from commons.cusntom.pagination import CustomPage


class ApplyView(CustomView):

    model = ApplyModel
    serializer_class = ApplySer
    permission_classes = []
    pagination_class = CustomPage
    fields = {
        "applyId": {
            "type": 'exact',
            "converter": int,
            "allow_empty": False
        },
        "applyName": {
            "type": 'icontains',
            "converter": str,
            "allow_empty": True
        }
    }


apply_view = ApplyView.as_view()
