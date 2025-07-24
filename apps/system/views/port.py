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
        }
    }
    index_key = 'portId'


port_view = PortView.as_view()

