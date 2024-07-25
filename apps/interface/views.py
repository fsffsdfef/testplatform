from django.shortcuts import render
from apps.interface.models.applymodel import Apply
from apps.interface.sers.applyser import ApplySer
from rest_framework.viewsets import ModelViewSet
# Create your views here.


class ApplyView(ModelViewSet):
    queryset = Apply.objects.all()
    serializer_class = ApplySer
