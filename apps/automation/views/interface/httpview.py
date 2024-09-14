from apps.automation.models.interface import InterfaceHttpCases
from apps.automation.sers.interface.httpser import InterfaceHttpSer
from rest_framework.viewsets import ModelViewSet
from utils.customview import CustomView
from utils.baseresponse import BasePage


class InterfaceHttpView(CustomView):
    queryset = InterfaceHttpCases.objects.all()
    serializer_class = InterfaceHttpSer
    permission_classes = []
    pagination_class = BasePage
