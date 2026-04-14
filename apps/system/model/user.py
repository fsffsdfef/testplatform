from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.hashers import make_password
from commons.abs.basemodel import BaseModel
from .depart_apply_port import DepartModel
from .permission_group_role import GroupModel, RoleModel


class UserModel(BaseModel, AbstractBaseUser):
    """用户模型"""
    userId = models.CharField(primary_key=True, max_length=30)
    userName = models.CharField(verbose_name='用户名', help_text='输入用户名', max_length=50)
    email = models.EmailField(verbose_name='邮箱', help_text='输入邮箱', unique=True, max_length=50)
    phone = models.CharField(verbose_name='手机号', help_text='输入手机号', unique=True, max_length=20)
    password = models.CharField(verbose_name='密码', help_text='输入密码', max_length=100)
    groups = models.ManyToManyField(to=GroupModel, related_name='user', blank=True)
    roles = models.ManyToManyField(to=RoleModel, related_name='user', blank=True)
    is_active = models.BooleanField(default=True)
    depart = models.ForeignKey(to=DepartModel, to_field='departId', related_name='user', on_delete=models.CASCADE)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['password']

    objects = BaseUserManager()

    class Meta:
        db_table = 't_user'

    def save(self, *args, **kwargs):
        if not self.userId:
            self.userId = self.get_random_number(field_name='userId', length=6, prefix='T')
        if not str(self.password).startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
