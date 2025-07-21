from django.db import models
from commons.abs.basemodel import BaseModel
from ..cases.model.interface_case import HttpCaseModel
# Create your models here.


class SuitModel(BaseModel):

    suitId = models.IntegerField(verbose_name='套件Id', primary_key=True)
    suitName = models.CharField(verbose_name='套件名', max_length=50)
    caseList = models.ManyToManyField(to=HttpCaseModel, related_name='suit', blank=True)

    class Meta:
        db_table = 't_suit'

    def __str__(self):
        return self.suitName

    def save(self, *args, **kwargs):
        if not self.suitId:
            self.suitId = self.get_random_number('suitId', None, None, 1000, 9999)
        super().save(*args, **kwargs)
