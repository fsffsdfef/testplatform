from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .sers import SuitSer
from .models import SuitModel
from commons.cusntom.pagination import CustomPage
from commons.cusntom.view import CustomView
# Create your views here.


class SuitView(CustomView):

    model = SuitModel
    serializer_class = SuitSer
    authentication_classes = []
    permission_classes = []
    pagination_class = CustomPage

    fields = {
        "suitId": {
            "type": 'exact',
            "converter": int,
            "allow_empty": False
        },
        "suitName": {
            "type": 'icontains',
            "converter": str,
            "allow_empty": True
        }
    }
    index_key = "suitId"


suit_view = SuitView.as_view()