from django.db import models
from commons.abs.basemodel import BaseModel
from .interface_case import HttpCaseModel


class ExpressItem(BaseModel):
    expressItemId = models.IntegerField('规则组id', primary_key=True)
    httpCase = models.ForeignKey(HttpCaseModel, to_field='caseId',
                                 related_name='expressItem', on_delete=models.CASCADE)

    class Meta:
        db_table = 't_express_item'

    def __str__(self):
        return str(self.expressItemId)

    def save(self, *args, **kwargs):
        if not self.expressItemId:
            self.expressItemId = self.get_random_number("expressItemId", None, None, 1000, 9999)
        super().save(*args, **kwargs)


class Expresses(BaseModel):
    expressId = models.IntegerField("表达式id", primary_key=True)
    matchKey = models.CharField('key', max_length=100, help_text='需要校验value的key')
    keyType = models.CharField('key的类型', max_length=30, help_text='key对应value的类型', default='str', null=True, blank=True)
    matchMethod = models.CharField('取值方法', max_length=200, null=True, blank=True)
    matchValue = models.CharField('预期答案', max_length=200, null=True, blank=True)
    matchOper = models.CharField('运算符', max_length=10, help_text='运算符')
    expressItem = models.ForeignKey(ExpressItem, to_field='expressItemId',
                                    related_name='expressList', on_delete=models.CASCADE)

    class Meta:
        db_table = 't_expresses'

    def __str__(self):
        return str(self.expressId)

    def save(self, *args, **kwargs):
        if not self.expressId:
            self.expressId = self.get_random_number("expressId", None, None, 1000, 9999)
        super().save(*args, **kwargs)
