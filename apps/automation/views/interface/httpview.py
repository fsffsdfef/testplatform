from apps.automation.models import InterfaceHttpCases
from apps.automation.sers.interface.httpser import InterfaceHttpSer
from rest_framework.viewsets import ModelViewSet


class InterfaceHttpView(ModelViewSet):
    queryset = InterfaceHttpCases.objects.all()
    serializer_class = InterfaceHttpSer
    permission_classes = []
