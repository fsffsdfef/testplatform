from django.db import models
from commons.abs.basemodel import BaseModel
from .permission_group_role import PermissionModel
import operator


class Menu(BaseModel):

    menuId = models.IntegerField('菜单ID', primary_key=True)
    menuName = models.CharField('菜单名', unique=True, max_length=50)
    icon = models.CharField('图标', max_length=20, null=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    per = models.ManyToManyField(to=PermissionModel, related_name='menu', blank=True)
    path = models.CharField(max_length=40, default='/home')
    sequence = models.IntegerField('排序', default=0)
    objects = models.Manager

    def get_children_tree(self, permission_list):
        """获取子菜单所有数据"""
        children = []
        menus = Menu.objects.filter(parent=self)
        for menu in menus:
            per_list = [per.perCode for per in menu.per.all()]
            set_per = set(per_list)
            set_user_per = set(permission_list)
            if len(set_user_per.union(set_per)) < len(per_list) + len(permission_list) or 'ADMIN' in permission_list:
                children.append({
                    'menuId': menu.menuId,
                    'menuName': menu.menuName,
                    'icon': menu.icon,
                    'path': menu.path,
                    'sequence': menu.sequence,
                    'children': menu.get_children_tree(permission_list)  # 使用递归逻辑获取更下层的菜单
                })
        children = sorted(children, key=operator.itemgetter("sequence"))
        return children

    def __str__(self):
        return self.menuName

    def save(self, *args, **kwargs):
        if not self.menuId:
            self.menuId = self.get_random_number("menuId", None, None, 1000, 9999)
        super().save(*args, **kwargs)
