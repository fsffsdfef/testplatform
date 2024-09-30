from utils.customview import CustomView
from ..modelss.depart_and_app import Depart, Menu, Apply
from ..sers.depart_app_menu_ser import DepartSer, MenuSer, ApplySer
from utils.baseresponse import BaseResponse
from rest_framework.views import APIView


class DepartView(CustomView):
    queryset = Depart.objects.all()
    serializer_class = DepartSer
    permission_classes = []


class ApplyView(CustomView):
    queryset = Apply.objects.all()
    serializer_class = ApplySer
    permission_classes = []


class MenuView(APIView):

    def get(self, request):
        top_menu = Menu.objects.filter(parent=None)
        menu_tree = []
        for menu in top_menu:
            menu_tree.append({
                'menu_id': menu.menu_id,
                'name': menu.name,
                'parent': menu.get_children_tree()
            })
        return BaseResponse(data=menu_tree)

    def post(self, request):
        data = request.data
        print(data)
        queryset = Menu.objects.filter(menu_id=data.get('menu_id')).first()
        ser = MenuSer(instance=queryset, data=data, partial=True)
        if ser.is_valid(raise_exception=True):
            ser.save()
            return BaseResponse(data=ser.data)
        else:
            return BaseResponse(data=ser.errors)


class MenuViewA(CustomView):
    queryset = Menu.objects.all()
    serializer_class = MenuSer


# class ExpressView(ModelViewSet):
#     queryset = Expresses.objects.all()
#     serializer_class = ExpressesSer
#     permission_classes = []
#
#
# class ExpressItemView(ModelViewSet):
#     queryset = ExpressItem.objects.all()
#     serializer_class = ExpressItemSer
#     permission_classes = []