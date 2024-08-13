from django.shortcuts import render
from apps.interface.models import *
from apps.interface.sers import *
from rest_framework.viewsets import ModelViewSet
# Create your viewsx here.


class ApplyView(ModelViewSet):
    queryset = Apply.objects.all()
    serializer_class = ApplySer


class PortView(ModelViewSet):
    queryset = Port.objects.all()
    serializer_class = PortSer
