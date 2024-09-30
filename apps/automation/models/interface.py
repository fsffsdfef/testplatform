from django.db import models
from apps.common.basemodel import BaseModel
from utils.random_number import RandomNumber
from apps.common.modelss.depart_and_app import Apply

class Port(models.Model):
    portName = models.CharField('接口名', max_length=30, help_text='接口名')
    method_choices = (('POST', 'post'), ('GET', 'get'), ('UPDATE', 'update'), ('DELETE', 'delete'))
    portMethod = models.CharField('请求方式', max_length=30, help_text='请求方式', choices=method_choices, default="POST")
    portIntroduction = models.CharField('接口介绍', max_length=100, help_text='接口介绍', null=True)
    apply = models.ForeignKey(Apply, to_field='appId', related_name='port', on_delete=models.CASCADE)

    class Meta:
        db_table = 'test_port'

    def __str__(self):
        return self.portName


class InterfaceHttpCases(BaseModel, RandomNumber):
    caseId = models.CharField('接口用例id', help_text='接口用例id', max_length=6, primary_key=True)
    caseName = models.CharField('用例名称', help_text='用例名称', max_length=50, unique=True)
    headers = models.JSONField('请求头', help_text='头部信息', null=True)
    body = models.JSONField('请求体', help_text='请求体', null=True)
    timeOut = models.IntegerField('超时时间', help_text='超时时间', default=5)
    retries = models.IntegerField('重试次数', help_text='重试次数', default=0)
    port = models.ForeignKey(Port, to_field='id', related_name='httpCase', on_delete=models.CASCADE)

    class Meta:
        db_table = 'interface_http_cases'

    def __str__(self):
        return self.caseName

    def save(self, *args, **kwargs):
        if not self.caseId:
            self.caseId = self.get_random_number(field_name='caseId', length=6)
            super().save(*args, **kwargs)


class ExpressItem(models.Model, RandomNumber):
    expressItemId = models.CharField('规则组id', max_length=8, primary_key=True)
    httpCase = models.ForeignKey(InterfaceHttpCases, to_field='caseId',
                                 related_name='expressItem', on_delete=models.CASCADE)

    class Meta:
        db_table = 'test_expressitem'

    def __str__(self):
        return self.expressItemId

    def save(self, *args, **kwargs):
        if not self.expressItemId:
            self.expressItemId = self.get_random_number(field_name='expressItemId', length=7)
        super().save(*args, **kwargs)


class Expresses(models.Model, RandomNumber):
    expressId = models.CharField("表达式", max_length=7, primary_key=True)
    matchKey = models.CharField('匹配建', max_length=20, help_text='需要校验的key')
    matchValue = models.CharField('匹配值', max_length=20, help_text='预期返回的值')
    keyType = models.CharField('字段类型', max_length=20, help_text='需断言字段的类型')
    matchOper = models.CharField('计算方法', max_length=10, help_text='运算校验的方法')
    expressItem = models.ForeignKey('ExpressItem', to_field='expressItemId',
                                    related_name='expressList', on_delete=models.CASCADE)

    class Meta:
        db_table = 'test_expresses'

    def __str__(self):
        return self.expressId

    def save(self, *args, **kwargs):
        if not self.expressId:
            self.expressId = self.get_random_number(field_name='expressId', length=7)
        super().save(*args, **kwargs)


