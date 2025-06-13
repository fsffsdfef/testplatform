from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import get_object_or_404, GenericAPIView
from rest_framework.response import Response
from commons.cusntom.response import CustomResponse
from commons.cusntom.pagination import CustomPage
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


class PerView(GenericAPIView):
    model = PermissionModel
    serializer_class = PerSer
    permission_classes = []
    pagination_class = CustomPage

    def post(self, request, *args, **kwargs):
        """
        post请求分流
        :param request: 入参
        :param args:
        :param kwargs:
        :return: 下发json格式数据
        """
        request_path = request.path
        request_data = request.data
        if request_path == "/api/per/getPageList":
            return self.get_query(request=request_data, *args, **kwargs)
        elif request_path == "/api/per/add":
            return self.add(request=request_data, *args, **kwargs)
        elif request_path == "/api/per/del":
            return self.delete(request=request_data, *args, **kwargs)
        elif request_path == "/api/per/update":
            return self.update(request=request_data, *args, **kwargs)
        return CustomResponse(data=[])

    def add(self, request, *args, **kwargs):
        ser = self.serializer_class(data=request)
        if ser.is_valid(raise_exception=True):
            ser.save()
            return CustomResponse(data=ser.data, msg="新建成功", code=101)

    def delete(self, request, *args, **kwargs):
        key = request.get("perId")
        if key is None:
            return CustomResponse(data=[], msg="perId为空", code=1001)
        self.model.objects.get(applyId=key).delete()
        return CustomResponse(data=[], msg="删除成功", code=201)

    def update(self, request, *args, **kwargs):
        key = request.pop("perId", None)
        model_obj = self.model.objects.get(pk=key)
        ser = self.serializer_class(instance=model_obj, data=request)
        if ser.is_valid(raise_exception=True):  # 校验数据是否满足条件
            ser.save()
            return CustomResponse(data=ser.data, msg="修改成功", code=1004)
        return CustomResponse(data=[], msg="修改失败", code=1004)

    def search(self, request, *args, **kwargs):
        return []

    def get_query(self, request, *args, **kwargs):
        apply_id = request.pop("perId", None)
        apply_name = request.get("perCode", None)
        if apply_id is not None and apply_name is not None:
            data = self.model.objects.filter(
                Q(perId=apply_id) &
                Q(perCode__icontains=apply_name)
            ).order_by("-updatedDate")
        elif apply_id is not None or apply_name is not None:
            data = self.model.objects.filter(
                Q(perId=apply_id) |
                Q(perCode__icontains=apply_name)
            ).order_by("-updatedDate")
        else:
            data = self.model.objects.all().order_by("-updatedDate")
        page_data = self.paginate_queryset(data)
        if page_data is not None:
            serializer = self.serializer_class(instance=page_data, many=True)
            return self.get_paginated_response(serializer.data)
        ser = self.serializer_class(instance=data, many=True)
        return CustomResponse(data=ser.data)


class RoleView(ModelViewSet):
    permission_classes = []
    queryset = RoleModel.objects.all()
    serializer_class = RoleSer


per_view = PerView.as_view()