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
    index_key = "applyId"
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
        },
        "owner": {
            "type": 'icontains',
            "converter": str,
            "allow_empty": True
        },
        "depart": {
            "type": 'icontains',
            "converter": int,
            "allow_empty": True,
            "related_field": "depart__departId",
            "related_lookup_type": 'icontains'
        },
        'departName': {
            'type': 'icontains',
            'converter': str,
            'allow_empty': False,
            'related_field': 'depart__departName',  # 假设ApplyModel有applyName字段
            'related_lookup_type': 'icontains'
        }
    }


apply_view = ApplyView.as_view()
