from django.db import models
from utils.random_number import RandomNumber
# Create your models here.


class BaseModel(models.Model, RandomNumber):
    created_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    updated_date = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    create_user = models.CharField(verbose_name='创建人', max_length=20)
    update_user = models.CharField(verbose_name='修改人', max_length=20)

    class Meta:
        abstract = True
        ordering = ["created_date"]


class Depart(BaseModel):
    depart_id = models.CharField(verbose_name='部门ID', primary_key=True, max_length=20)
    depart_name = models.CharField(verbose_name='部门名', max_length=30)

    class Meta:
        db_table = 't_depart'

    def __str__(self):
        return self.depart_name

    def save(self, *args, **kwargs):
        if not self.depart_id:
            self.depart_id = self.get_random_number(field_name='depart_id', length=6)
        super().save(*args, **kwargs)
