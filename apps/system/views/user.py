from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from rest_framework.generics import GenericAPIView
from commons.cusntom.response import CustomResponse
from django.db.models import Q
from commons.cusntom.pagination import CustomPage
from commons.cusntom.view import CustomView
from ..sers.user_jws import *


class TokenView(TokenObtainPairView):
    permission_classes = [AllowAny, ]
    serializer_class = TokenSer


class UserView(GenericAPIView):
    model = UserModel
    serializer_class = UserSer
    permission_classes = []
    pagination_class = CustomPage
    fields = {
        "userId": {
            "type": 'exact',
            "converter": int,
            "allow_empty": False
        },
        "email": {
            "type": 'exact',
            "converter": int,
            "allow_empty": False
        },
        "userName": {
            "type": 'icontains',
            "converter": str,
            "allow_empty": True
        }
    }

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
        if request_path == "/api/user/getPageList":
            return self.get_query(request=request_data, *args, **kwargs)
        elif request_path == "/api/user/add":
            return self.add(request=request_data, *args, **kwargs)
        elif request_path == "/api/user/del":
            return self.delete(request=request_data, *args, **kwargs)
        elif request_path == "/api/user/update":
            return self.update(request=request_data, *args, **kwargs)
        return CustomResponse(data=[])

    def add(self, request, *args, **kwargs):
        ser = self.serializer_class(data=request)
        if ser.is_valid(raise_exception=True):
            ser.save()
            return CustomResponse(data=ser.data, msg="新建成功", code=101)

    def delete(self, request, *args, **kwargs):
        key = request.get("userId")
        if key is None:
            return CustomResponse(data=[], msg="userId为空", code=1001)
        self.model.objects.get(caseId=key).delete()
        return CustomResponse(data=[], msg="删除成功", code=201)

    def update(self, request, *args, **kwargs):
        key = request.pop("userId", None)
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
            'userId': request.pop("userId", None),
            'email': request.get("email", None)
        }
        q_objects = Q()
        if query_params['userId'] not in (None, ''):
            case_id = int(query_params['userId'])
            q_objects &= Q(userId=case_id)
        email = query_params['email']
        if email is not None:  # 明确处理 null 和空字符串
            q_objects &= Q(email__icontains=email)
        queryset = self.model.objects.all()
        if _ := q_objects.children:
            queryset = queryset.filter(q_objects)
        ordered_queryset = queryset.order_by("-updatedDate")
        page_data = self.paginate_queryset(ordered_queryset)
        if page_data is not None:
            serializer = self.serializer_class(instance=page_data, many=True)
            return self.get_paginated_response(serializer.data)
        ser = self.serializer_class(instance=ordered_queryset, many=True)
        return CustomResponse(data=ser.data)


user_view = UserView.as_view()
