from ..model.meu import Menu
from ..sers.menu import MenuSer
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import GenericAPIView
from django.db.models import Q
from commons.cusntom.view import CustomView
from commons.cusntom.response import CustomResponse
from commons.cusntom.pagination import CustomPage
from commons.utils.analysis_token import get_token
from celerys.tasks import demo
from celery import result


class MenuInitializeView(ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSer
    pagination_class = CustomPage
    permission_classes = []

    def list(self, request, *args, **kwargs):
        menus = self.serializer_class.Meta.model.objects.filter(parent=None)
        menu_tree = []
        menu_sort_tree = []
        permission_list = get_token(request)['permissionList']
        for menu in menus:
            per_list = [per.perCode for per in menu.per.all()]
            set_per = set(per_list)
            set_user_per = set(permission_list)
            if len(set_user_per.union(set_per)) < len(per_list) + len(permission_list) or 'ADMIN' in permission_list:
                menu_tree.append({
                    "menuId": menu.menuId,
                    'menuName': menu.menuName,
                    'icon': menu.icon,
                    'path': menu.path,
                    'sequence': menu.sequence,
                    'children': menu.get_children_tree(permission_list)
                })
        return CustomResponse(data=menu_tree, msg='true')


class MenuCascaderView(ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSer
    permission_classes = []
    authentication_classes = []

    # def list(self, request, *args, **kwargs):
    #     menus = self.queryset.filter(parent=None)
    #     menu_tree = []
    #     for menu in menus:
    #         item_obj = dict()
    #         item_obj['menuId'] = menu.menuId
    #         item_obj['menuName'] = menu.menuName
    #         item_obj['children'] = []
    #         children_list = self.queryset.filter(parent=menu.menuId)
    #         for children in children_list:
    #             children_obj = dict()
    #             children_obj['menuId'] = children.menuId
    #             children_obj['menuName'] = children.menuName
    #             item_obj['children'].append(children_obj)
    #         menu_tree.append(item_obj)
    #     print(menu_tree)
    #
    #     return CustomResponse(data=menu_tree, msg='true')


class MenuView(CustomView):
    model = Menu
    serializer_class = MenuSer
    permission_classes = []
    throttle_classes = []
    pagination_class = CustomPage
    fields = {
        "menuId": {
            "type": 'exact',
            "converter": int,
            "allow_empty": False
        },
        "menuName": {
            "type": 'icontains',
            "converter": str,
            "allow_empty": True
        }
    }
    index_key = "menuId"

    # def post(self, request, *args, **kwargs):
    #     """
    #     post请求分流
    #     :param request: 入参
    #     :param args:
    #     :param kwargs:
    #     :return: 下发json格式数据
    #     """
    #     request_path = request.path
    #     request_data = request.data
    #     if request_path == "/api/menu/getPageList":
    #         # res = demo.delay(12, 12)
    #         # print(f'res: {res.get()}')
    #         return self.get_query(request=request_data, *args, **kwargs)
    #     elif request_path == "/api/menu/add":
    #         return self.add(request=request_data, *args, **kwargs)
    #     elif request_path == "/api/menu/del":
    #         return self.delete(request=request_data, *args, **kwargs)
    #     elif request_path == "/api/menu/update":
    #         return self.update(request=request_data, *args, **kwargs)
    #     return CustomResponse(data=[])
    #
    # def add(self, request, *args, **kwargs):
    #     ser = self.serializer_class(data=request)
    #     if ser.is_valid(raise_exception=True):
    #         ser.save()
    #         return CustomResponse(data=ser.data, msg="新建成功", code=101)
    #
    # def delete(self, request, *args, **kwargs):
    #     key = request.get("menuId")
    #     if key is None:
    #         return CustomResponse(data=[], msg="menuId为空", code=1001)
    #     self.model.objects.get(applyId=key).delete()
    #     return CustomResponse(data=[], msg="删除成功", code=201)
    #
    # def update(self, request, *args, **kwargs):
    #     key = request.pop("menuId", None)
    #     model_obj = self.model.objects.get(pk=key)
    #     ser = self.serializer_class(instance=model_obj, data=request)
    #     if ser.is_valid(raise_exception=True):  # 校验数据是否满足条件
    #         ser.save()
    #         return CustomResponse(data=ser.data, msg="修改成功", code=1004)
    #     return CustomResponse(data=[], msg="修改失败", code=1004)
    #
    # def search(self, request, *args, **kwargs):
    #     return []
    #
    # def get_query(self, request, *args, **kwargs):
    #     depart_id = request.pop("menuId", None)
    #     depart_name = request.get("menuName", None)
    #     if depart_id is not None and depart_name is not None:
    #         data = self.model.objects.filter(
    #             Q(menuId=depart_id) &
    #             Q(menuName__icontains=depart_name)
    #         ).order_by("-updatedDate")
    #     elif depart_id is not None or depart_name is not None:
    #         data = self.model.objects.filter(
    #             Q(menuId=depart_id) |
    #             Q(menuName__icontains=depart_name)
    #         ).order_by("-updatedDate")
    #     else:
    #         data = self.model.objects.all().order_by("-updatedDate")
    #     page_data = self.paginate_queryset(data)
    #     if page_data is not None:
    #         serializer = self.serializer_class(instance=page_data, many=True)
    #         return self.get_paginated_response(serializer.data)
    #     ser = self.serializer_class(instance=data, many=True)
    #     return CustomResponse(data=ser.data)


menu_view = MenuView.as_view()
