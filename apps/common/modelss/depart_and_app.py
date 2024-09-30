from django.db import models
from utils.random_number import RandomNumber
from apps.common.basemodel import BaseModel
# Create your db here.


class Depart(BaseModel, RandomNumber):
    """部门数据模型"""
    depart_id = models.CharField(verbose_name='部门ID', primary_key=True, max_length=20)
    depart_name = models.CharField(verbose_name='部门名', max_length=30)

    class Meta:
        db_table = 't_depart'

    def __str__(self):
        return self.depart_name

    def save(self, *args, **kwargs):
        if not self.depart_id:
            self.depart_id = self.get_random_number(field_name='depart_id', length=6)
        super().save(*args, **kwargs)


class Apply(BaseModel, RandomNumber):
    """应用数据模型"""
    appId = models.CharField(max_length=100, primary_key=True)
    appName = models.CharField(verbose_name='应用名', max_length=30, unique=True)
    appType = models.CharField(verbose_name='服务类型', max_length=10, choices=((0, 'http'), (1, 'dubbo')), default=0)
    domains = models.URLField(verbose_name='域名', unique=True)
    depart = models.ForeignKey(to=Depart, to_field='depart_id', related_name='app', on_delete=models.CASCADE)

    class Meta:
        db_table = 't_apply'

    def __str__(self):
        return self.appName

    def save(self, *args, **kwargs):
        if not self.appId:
            self.appId = self.get_random_number(field_name='appId', length=5, prefix='1000')
        super().save(*args, **kwargs)


class Menu(BaseModel, RandomNumber):
    menu_id = models.CharField(verbose_name='菜单id', max_length=8, primary_key=True)
    name = models.CharField(verbose_name='菜单名', max_length=30)
    #  使用自关联逻辑，parent为上层菜单id
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

    objects = models.Manager

    def get_children_tree(self):
        """获取子菜单所有数据"""
        children = []
        menus = Menu.objects.filter(parent=self)
        for menu in menus:
            children.append({
                'menu_id': menu.menu_id,
                'name': menu.name,
                'parent': menu.get_children_tree()   # 使用递归逻辑获取更下层的菜单
            })
        return children

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.menu_id:
            self.menu_id = self.get_random_number(field_name='menu_id', length=5)
        super().save(*args, **kwargs)
        


