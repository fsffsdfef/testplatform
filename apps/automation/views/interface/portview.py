from rest_framework.viewsets import ModelViewSet
from apps.automation.models.interface import Port
from apps.automation.sers.interface.portser import PortSer


class PortView(ModelViewSet):
    queryset = Port.objects.all()
    serializer_class = PortSer
    permission_classes = []
