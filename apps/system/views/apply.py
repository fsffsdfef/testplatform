from rest_framework.generics import GenericAPIView
from django.db.models import Q
from ..sers.depart_apply_port import *
from commons.cusntom.response import CustomResponse
from commons.cusntom.pagination import CustomPage


class ApplyView(GenericAPIView):

    model = ApplyModel
    serializer_class = ApplySer
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
        if request_path == "/api/apply/getPageList":
            return self.get_query(request=request_data, *args, **kwargs)
        elif request_path == "/api/apply/add":
            return self.add(request=request_data, *args, **kwargs)
        elif request_path == "/api/apply/del":
            return self.delete(request=request_data, *args, **kwargs)
        elif request_path == "/api/apply/update":
            return self.update(request=request_data, *args, **kwargs)
        return CustomResponse(data=[])

    def add(self, request, *args, **kwargs):
        ser = self.serializer_class(data=request)
        if ser.is_valid(raise_exception=True):
            ser.save()
            return CustomResponse(data=ser.data, msg="新建成功", code=101)

    def delete(self, request, *args, **kwargs):
        key = request.get("applyId")
        if key is None:
            return CustomResponse(data=[], msg="applyId为空", code=1001)
        self.model.objects.get(applyId=key).delete()
        return CustomResponse(data=[], msg="删除成功", code=201)

    def update(self, request, *args, **kwargs):
        key = request.pop("applyId", None)
        print(request)
        model_obj = self.model.objects.get(pk=key)
        ser = self.serializer_class(instance=model_obj, data=request)
        if ser.is_valid(raise_exception=True):  # 校验数据是否满足条件
            ser.save()
            return CustomResponse(data=ser.data, msg="修改成功", code=1004)
        return CustomResponse(data=[], msg="修改失败", code=1004)

    def search(self, request, *args, **kwargs):
        return []

    def get_query(self, request, *args, **kwargs):
        apply_id = request.pop("applyId", None)
        apply_name = request.get("applyName", None)
        if apply_id is not None and apply_name is not None:
            data = self.model.objects.filter(
                Q(applyId=apply_id) &
                Q(applyName__icontains=apply_name)
            ).order_by("-updatedDate")
        elif apply_id is not None or apply_name is not None:
            data = self.model.objects.filter(
                Q(applyId=apply_id) |
                Q(applyName__icontains=apply_name)
            ).order_by("-updatedDate")
        else:
            data = self.model.objects.all().order_by("-updatedDate")
        page_data = self.paginate_queryset(data)
        if page_data is not None:
            serializer = self.serializer_class(instance=page_data, many=True)
            return self.get_paginated_response(serializer.data)
        ser = self.serializer_class(instance=data, many=True)
        return CustomResponse(data=ser.data)


apply_view = ApplyView.as_view()
