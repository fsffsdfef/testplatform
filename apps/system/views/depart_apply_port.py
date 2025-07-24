from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import get_object_or_404, GenericAPIView
from commons.cusntom.response import CustomResponse
from commons.cusntom.pagination import CustomPage
from commons.cusntom.view import CustomView
from ..model.depart_apply_port import *
from ..sers.depart_apply_port import *
from django.db.models import Q


# class DepartView(GenericAPIView):
#     queryset = DepartModel
#     serializer_class = DepartSer
#     permission_classes = []
#
#     def post(self, request, *args, **kwargs):
#         depart_id = request.data.get("departId", None)
#         print(f"path:{request.path}")
#         if request.path == "/api/search":
#             return self.get_test_data(request, *args, **kwargs)
#         elif depart_id:
#             data = self.queryset.objects.filter(departId=depart_id)
#             ser = DepartSer(instance=data, many=True)
#             return Response({"data": ser.data})
#         return Response({"data": []})
#
#     def get_search(self, request, *args, **kwargs):
#         data = request.data.get("wula", None)
#         return Response({"data": data})


class ApplyView(ModelViewSet):
    queryset = ApplyModel.objects.all()
    permission_classes = []
    serializer_class = ApplySer


class PortView(ModelViewSet):
    permission_classes = []
    queryset = PortModel.objects.all()
    serializer_class = PortSer


# class PerView(ModelViewSet):
#     permission_classes = []
#     queryset = PermissionModel.objects.all()
#     serializer_class = PerSer
#
#     def list(self, request, *args, **kwargs):
#         queryset = self.filter_queryset(self.get_queryset())
#
#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)
#
#         serializer = self.get_serializer(queryset, many=True)
#         return CustomResponse(data=serializer.data)


class PerView(CustomView):
    model = PermissionModel
    serializer_class = PerSer
    permission_classes = []
    pagination_class = CustomPage
    fields = {
        "perId": {
            "type": 'exact',
            "converter": int,
            "allow_empty": False
        },
        "perCode": {
            "type": 'icontains',
            "converter": str,
            "allow_empty": False
        },
    }


class RoleView(CustomView):
    model = RoleModel
    serializer_class = RoleSer
    permission_classes = []
    pagination_class = CustomPage
    fields = {
        "roleId": {
            "type": 'exact',
            "converter": int,
            "allow_empty": False
        },
        "roleName": {
            "type": 'icontains',
            "converter": str,
            "allow_empty": False
        },
    }


class GroupsView(CustomView):
    model = GroupModel
    serializer_class = GroupSer
    permission_classes = []
    pagination_class = CustomPage
    fields = {
        "groupId": {
            "type": 'exact',
            "converter": int,
            "allow_empty": False
        },
        "groupName": {
            "type": 'icontains',
            "converter": str,
            "allow_empty": False
        },
    }


per_view = PerView.as_view()
role_view = RoleView.as_view()
group_view = GroupsView.as_view()
