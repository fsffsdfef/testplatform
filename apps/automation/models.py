from django.db import models
from apps.common.basemodel import BaseModel
from utils.random_number import RandomNumber


class InterfaceHttpCases(BaseModel, RandomNumber):
    caseId = models.CharField('接口用例id', help_text='接口用例id', max_length=6, primary_key=True)
    caseName = models.CharField('用例名称', help_text='用例名称', max_length=50, unique=True)
    headers = models.JSONField('请求头', help_text='头部信息', null=True)
    body = models.JSONField('请求体', help_text='请求体', null=True)
    timeOut = models.IntegerField('超时时间', help_text='超时时间', default=5)
    retries = models.IntegerField('重试次数', help_text='重试次数', default=0)

    class Meta:
        db_table = 'interface_http_cases'

    def __str__(self):
        return self.caseName

    def save(self, *args, **kwargs):
        if not self.caseId:
            self.caseId = self.get_random_number(field_name='caseId', length=6)
            super().save(*args, **kwargs)


