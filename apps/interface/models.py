from apps.management.models import BaseModel, Apply
from django.db import models


class Port(BaseModel):
    """接口数据模型"""
    port_id = models.CharField(verbose_name='接口id', primary_key=True, max_length=30)
    port_name = models.CharField(verbose_name='接口名', max_length=30, unique=True)
    method = models.CharField(verbose_name='请求方法', max_length=5, choices=(('get', 'get'), ('post', 'post')))
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


class HttpCase(BaseModel):
    """http类型接口用例"""
    case_id = models.CharField(verbose_name='用例id', max_length=10, primary_key=True)
    case_name = models.CharField(verbose_name='用例名称', max_length=200, unique=True)
    header = models.JSONField(verbose_name='头部信息', null=True)
    res = models.JSONField(verbose_name='入参', max_length=1000, null=True)
    time_out = models.IntegerField(verbose_name='超时时间', default=3)
    total = models.IntegerField(verbose_name='重试次数', default=0)
    iscore = models.BooleanField(verbose_name='核心用例', default=False)
    verify = models.JSONField(verbose_name='断言数据', max_length=200)

    class Meta:
        db_table = 't_http_case'

    def __str__(self):
        return self.case_name

    def save(self, *args, **kwargs):
        if not self.case_id:
            self.case_id = self.get_random_number(field_name='case_id', length=5)
        super().save(*args, **kwargs)


class DubboCase(BaseModel):
    """Dubbo类型接口用例"""
    pass
