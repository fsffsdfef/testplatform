from apps.common.basemodel import BaseModel
from utils.random_number import RandomNumber
from django.db import models


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


