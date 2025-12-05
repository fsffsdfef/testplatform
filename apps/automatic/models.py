from django.db import models
from django.core.exceptions import ValidationError
from commons.abs.basemodel import BaseModel
from ..cases.model.interface_case import HttpCaseModel
# Create your models here.


class SuitModel(BaseModel):

    suitId = models.IntegerField(verbose_name='套件Id', primary_key=True)
    suitName = models.CharField(verbose_name='套件名', max_length=50)
    casesList = models.ManyToManyField(to=HttpCaseModel, through='SuitCaseModel', related_name='suit', blank=True)

    class Meta:
        db_table = 't_suit'

    def __str__(self):
        return self.suitName

    def save(self, *args, **kwargs):
        if not self.suitId:
            self.suitId = self.get_random_number('suitId', None, None, 1000, 9999)
        super().save(*args, **kwargs)

    def get_ordered_cases(self):
        """获取按执行顺序排列的用例"""
        return self.casesList.through.objects.filter(suit=self).order_by('execution_order')

    def add_case_with_order(self, case, execution_order=None, is_first=False, is_last=False):
        """添加用例并设置执行顺序"""
        if execution_order is None:
            # 如果没有指定顺序，自动分配下一个顺序号
            max_order = self.casesList.through.objects.filter(suit=self).aggregate(
                max_order=models.Max('execution_order')
            )['max_order'] or 0
            execution_order = max_order + 1

        return self.casesList.through.objects.create(
            suit=self,
            case=case,
            execution_order=execution_order,
            is_first=is_first,
            is_last=is_last
        )


class SuitCaseModel(models.Model):
    """套件用例关联模型 - 用于存储用例在套件中的执行顺序"""
    suit = models.ForeignKey(SuitModel, on_delete=models.CASCADE, verbose_name='套件')
    case = models.ForeignKey(HttpCaseModel, on_delete=models.CASCADE, verbose_name='用例')
    execution_order = models.IntegerField(verbose_name='执行顺序', help_text='用例在套件中的执行顺序，数字越小越先执行')
    is_first = models.BooleanField(verbose_name='是否最先执行', default=False, help_text='标记为最先执行的用例')
    is_last = models.BooleanField(verbose_name='是否最后执行', default=False, help_text='标记为最后执行的用例')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 't_suit_case'
        unique_together = [['suit', 'case']]  # 确保同一套件中用例不重复
        ordering = ['execution_order', 'id']

    def __str__(self):
        return f"{self.suit.suitName} - {self.case.caseName} (顺序: {self.execution_order})"

    def clean(self):
        """验证逻辑"""
        # 检查同一套件中不能有多个最先执行或最后执行的用例
        if self.is_first:
            existing_first = SuitCaseModel.objects.filter(
                suit=self.suit,
                is_first=True
            ).exclude(pk=self.pk)
            if existing_first.exists():
                raise ValidationError('同一套件中只能有一个最先执行的用例')

        if self.is_last:
            existing_last = SuitCaseModel.objects.filter(
                suit=self.suit,
                is_last=True
            ).exclude(pk=self.pk)
            if existing_last.exists():
                raise ValidationError('同一套件中只能有一个最后执行的用例')


