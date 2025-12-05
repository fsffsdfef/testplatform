from ..sers.depart_apply_port import *
from commons.cusntom.view import CustomView
from commons.cusntom.pagination import CustomPage


class PortView(CustomView):

    model = PortModel
    serializer_class = PortSer
    permission_classes = []
    pagination_class = CustomPage
    fields = {
        "portId": {
            "type": 'exact',
            "converter": int,
            "allow_empty": False
        },
        "portName": {
            "type": 'icontains',
            "converter": str,
            "allow_empty": True
        },
        "apply": {
            "type": 'icontains',
            "converter": int,
            "allow_empty": True,
            "related_field": "apply__applyId",
            "related_lookup_type": 'icontains'
        },
        'applyName': {
            'type': 'icontains',
            'converter': str,
            'allow_empty': False,
            'related_field': 'apply__applyName',  # 假设ApplyModel有applyName字段
            'related_lookup_type': 'icontains'
        }
    }
    index_key = 'portId'


port_view = PortView.as_view()

