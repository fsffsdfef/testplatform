from django.db import models
from commons.abs.basemodel import BaseModel
from apps.system.model.depart_apply_port import PortModel


class HttpCaseModel(BaseModel):
    """http协议接口用例模型"""
    caseId = models.IntegerField(primary_key=True)
    caseName = models.CharField(verbose_name='用例名', help_text='输入用例名', max_length=100, unique=True)
    headers = models.JSONField(verbose_name='请求头', help_text='输入请求头部信息', null=True)
    body = models.JSONField(verbose_name='请求体', help_text='输入请求体信息', null=True)
    timeOut = models.IntegerField(verbose_name='超时时间', help_text='请输入超时时间', default=3)
    retries = models.IntegerField(verbose_name='重试次数', help_text='输入重视次数', default=1)
    isCore = models.BooleanField(verbose_name='是否为核心用例', default=False)
    port = models.ForeignKey(PortModel, to_field='portId', related_name='httpcase', on_delete=models.CASCADE)

    class Meta:
        db_table = 't_interface_httpcase'

    def __str__(self):
        return self.caseName

    def save(self, *args, **kwargs):
        if not self.caseId:
            self.caseId = self.get_random_number("caseId", None, None, 1000, 9999)
        super().save(*args, **kwargs)
