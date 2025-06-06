from rest_framework.generics import GenericAPIView
from django.db.models import Q
from ..sers.interface_case_ser import *
from commons.cusntom.response import CustomResponse
from commons.cusntom.pagination import CustomPage


class InterfaceView(GenericAPIView):

    model = HttpCaseModel
    serializer_class = HttpCaseSer
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
        if request_path == "/api/httpcase/getPageList":
            return self.get_query(request=request_data, *args, **kwargs)
        elif request_path == "/api/httpcase/add":
            return self.add(request=request_data, *args, **kwargs)
        elif request_path == "/api/httpcase/del":
            return self.delete(request=request_data, *args, **kwargs)
        elif request_path == "/api/httpcase/update":
            return self.update(request=request_data, *args, **kwargs)
        return CustomResponse(data=[])

    def add(self, request, *args, **kwargs):
        ser = self.serializer_class(data=request)
        if ser.is_valid(raise_exception=True):
            ser.save()
            return CustomResponse(data=ser.data, msg="新建成功", code=101)

    def delete(self, request, *args, **kwargs):
        key = request.get("caseId")
        if key is None:
            return CustomResponse(data=[], msg="caseId为空", code=1001)
        self.model.objects.get(caseId=key).delete()
        return CustomResponse(data=[], msg="删除成功", code=201)

    def update(self, request, *args, **kwargs):
        key = request.pop("caseId", None)
        model_obj = self.model.objects.get(pk=key)
        ser = self.serializer_class(instance=model_obj, data=request)
        if ser.is_valid(raise_exception=True):  # 校验数据是否满足条件
            ser.save()
            return CustomResponse(data=ser.data, msg="修改成功", code=1004)
        return CustomResponse(data=[], msg="修改失败", code=1004)

    def search(self, request, *args, **kwargs):
        return []

    def get_query(self, request, *args, **kwargs):
        query_params = {
            'caseId': request.pop("caseId", None),
            'caseName': request.get("caseName", None)
        }
        q_objects = Q()
        if query_params['caseId'] not in (None, ''):
            case_id = int(query_params['caseId'])
            q_objects &= Q(caseId=case_id)
        case_name = query_params['caseName']
        if case_name is not None:  # 明确处理 null 和空字符串
            q_objects &= Q(caseName__icontains=case_name)
        queryset = self.model.objects.all()
        if _  := q_objects.children:
            queryset = queryset.filter(q_objects)
        ordered_queryset = queryset.order_by("-updatedDate")
        page_data = self.paginate_queryset(ordered_queryset)
        if page_data is not None:
            serializer = self.serializer_class(instance=page_data, many=True)
            return self.get_paginated_response(serializer.data)
        ser = self.serializer_class(instance=ordered_queryset, many=True)
        return CustomResponse(data=ser.data)


httpcase_view = InterfaceView.as_view()
