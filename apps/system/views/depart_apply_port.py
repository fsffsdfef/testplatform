from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import get_object_or_404, GenericAPIView
from rest_framework.response import Response
from ..model.depart_apply_port import *
from ..sers.depart_apply_port import *


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
    serializer_class = ApplySer


class PortView(ModelViewSet):
    queryset = PortModel.objects.all()
    serializer_class = PortSer
