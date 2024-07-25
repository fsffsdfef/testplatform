from django.shortcuts import render
from apps.management.models import *
from apps.management.sers.departser import *
from rest_framework.viewsets import ModelViewSet
# Create your views here.


class DepartView(ModelViewSet):
    queryset = Depart.objects.all()
    serializer_class = DepartSer



