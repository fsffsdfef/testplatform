from apps.management.models import BaseModel, Depart
from django.db import models


class Apply(BaseModel):
    """app数据模型"""
    app_id = models.CharField(max_length=100, primary_key=True)
    app_name = models.CharField(verbose_name='应用名', max_length=30, unique=True)
    domains = models.URLField(verbose_name='域名', unique=True)
    depart = models.ForeignKey(to=Depart, to_field='depart_id', related_name='app', on_delete=models.CASCADE)

    class Meta:
        db_table = 't_apply'

    def __str__(self):
        return self.app_name

    def save(self, *args, **kwargs):
        if not self.app_id:
            self.app_id = self.get_random_number(field_name='app_id', length=5, prefix='1000')
        super().save(*args, **kwargs)


class Port(BaseModel):
    """接口数据模型"""
    port_id = models.CharField(verbose_name='接口id', primary_key=True, max_length=30)
    port_name = models.CharField(verbose_name='接口名', max_length=30, unique=True)
    port_type = models.CharField(verbose_name='接口类型', max_length=10, choices=(('http', 0), ('dubbo', 1)), default=0)
    port_intro = models.CharField(verbose_name='接口简介', max_length=200, null=True)
    apply = models.ForeignKey(to=Apply, to_field='app_id', related_name='port', on_delete=models.CASCADE)

    class Meta:
        db_table = 't_port'

    def __str__(self):
        return self.port_name

    def save(self, *args, **kwargs):
        if not self.port_id:
            self.port_id = self.get_random_number(field_name='port_id', length=5)
        super().save(*args, **kwargs)