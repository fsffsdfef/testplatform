from django.shortcuts import render
from apps.common.sers.departser import *
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework import status
from utils.baseresponse import BasePage


class Edit(BasePermission):

    def has_permission(self, request, view):
        data = request.data
        print(data.get('username'))
        if data.get('username') == '范胜威':
            raise exceptions.PermissionDenied({'msg': '不给你新增，气死你'})
        else:
            return True

    def has_object_permission(self, request, view, obj):
        return True


class UserView(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSer
    # pagination_class = BasePage
    permission_classes = [Edit]
    # permission_classes = []



