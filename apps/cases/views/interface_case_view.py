from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import GenericAPIView
from ..model.interface_case import *
from ..sers.interface_case_ser import *


class HttpCaseView(ModelViewSet):
    permission_classes = []
    queryset = HttpCaseModel.objects.all()
    serializer_class = HttpCaseSer


class ExpressItemView(ModelViewSet):
    permission_classes = []
    queryset = ExpressItem.objects.all()
    serializer_class = ExpressItemSer


class ExpressView(ModelViewSet):
    permission_classes = []
    queryset = Expresses.objects.all()
    serializer_class = ExpressSer
