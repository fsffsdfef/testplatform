from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.base_user import BaseUserManager
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


class Permission(BaseModel, RandomNumber):
    """权限数据模型"""
    p_id = models.CharField(verbose_name='权限id', primary_key=True, max_length=10)
    name = models.CharField(verbose_name='权限名', max_length=30, unique=True)

    class Meta:
        db_table = 't_permission'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.p_id:
            self.p_id = self.get_random_number(field_name='p_id', length=5)
        super().save(*args, **kwargs)


class Role(BaseModel, RandomNumber):
    """角色数据模型"""
    role_id = models.CharField(verbose_name='角色id', primary_key=True, max_length=10)
    name = models.CharField(verbose_name='角色名', max_length=30)
    permission = models.ManyToManyField(to=Permission, related_name='role', blank=True)

    class Meta:
        db_table = 't_role'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.role_id:
            self.role_id = self.get_random_number(field_name='role_id', length=5)
        super().save(*args, **kwargs)


class Group(BaseModel, RandomNumber):
    """分组数据模型"""
    group_id = models.CharField(verbose_name='分组id', primary_key=True, max_length=10)
    name = models.CharField(verbose_name='分组名', max_length=30)
    permission = models.ManyToManyField(to=Permission, related_name='group', blank=True)

    class Meta:
        db_table = 't_group'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.group_id:
            self.group_id = self.get_random_number(field_name='group_id', length=5)
        super().save(*args, **kwargs)


class User(BaseModel, AbstractBaseUser, RandomNumber):
    """用户模型"""
    user_id = models.CharField(verbose_name='用户id', primary_key=True, max_length=200)
    username = models.CharField(verbose_name='用户名', max_length=30)
    password = models.CharField(verbose_name='密码', max_length=100)
    email = models.EmailField(verbose_name='邮箱', unique=True, max_length=50)
    phone_number = models.CharField(verbose_name='手机号码', unique=True, max_length=15)
    role = models.ManyToManyField(to=Role, related_name='user', blank=True)
    group = models.ManyToManyField(to=Group, related_name='user', blank=True)
    permission = models.ManyToManyField(to=Permission, related_name='user', blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']

    objects = BaseUserManager()

    class Meta:
        db_table = 't_user'

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = self.get_random_number(field_name='user_id', length=5, prefix='TR')
        if not str(self.password).startswith('pbkdf2_'):
            self.password = make_password(self.password)
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


