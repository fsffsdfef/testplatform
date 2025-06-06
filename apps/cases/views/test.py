from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from commons.cusntom.response import CustomResponse
from ..sers.test import *
from django.db import transaction


class OneModelView(ModelViewSet):
    queryset = OneModel.objects.all()
    serializer_class = OneModelSer
    permission_classes = []
    authentication_classes = []

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        # 强制启用批量序列化器
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        try:
            self.perform_create(serializer)
        except Exception as e:
            return CustomResponse(
                {"error": str(e)}
            )

        # ✅ 获取创建的实例数据
        return CustomResponse(serializer.data)

    def perform_create(self, serializer):
        # ✅ 显式调用save()触发create方法
        serializer.save()


class TwoModelView(ModelViewSet):
    queryset = TwoModel.objects.all()
    serializer_class = TwoModelSer
    permission_classes = []


class ThreeModelView(ModelViewSet):
    queryset = ThreeModel.objects.all()
    serializer_class = ThreeModelSer
    permission_classes = []

