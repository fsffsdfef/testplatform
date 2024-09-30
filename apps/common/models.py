from django.db import models
from utils.random_number import RandomNumber
from apps.common.basemodel import BaseModel
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from apps.common.modelss.roles_permissions_group import *


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
