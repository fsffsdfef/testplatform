from ..sers.depart_apply_port import *
from commons.cusntom.pagination import CustomPage
from commons.cusntom.view import CustomView


class DepartView(CustomView):

    model = DepartModel
    serializer_class = DepartSer
    permission_classes = []
    pagination_class = CustomPage
    fields = {
        "departId": {
            "type": 'exact',
            "converter": int,
            "allow_empty": False
        },
        "departName": {
            "type": 'icontains',
            "converter": str,
            "allow_empty": True
        }
    }
    index_key = "departId"


depart_view = DepartView.as_view()
