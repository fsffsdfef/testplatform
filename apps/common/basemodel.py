from django.db import models


class BaseModel(models.Model):
    """抽象类"""
    created_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    updated_date = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    create_user = models.CharField(verbose_name='创建人', max_length=20)
    update_user = models.CharField(verbose_name='修改人', max_length=20)

    class Meta:
        abstract = True
        ordering = ["created_date"]
