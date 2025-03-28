from django.db import models
from commons.abs.basemodel import BaseModel


class DepartModel(BaseModel):
    """
    部门模型
    """
    departId = models.IntegerField(verbose_name="部门ID", primary_key=True)
    departName = models.CharField(verbose_name="部门名", max_length=40)

    class Meta:
        db_table = "t_depart"

    def __str__(self):
        return self.departName

    def save(self, *args, **kwargs):
        if not self.departId:
            self.departId = self.get_random_number("departId", None, None, 1000, 9999)
        super().save(*args, **kwargs)


class ApplyModel(BaseModel):
    """
    应用模型
    """
    applyId = models.IntegerField(verbose_name="应用Id", primary_key=True)
    applyName = models.CharField(verbose_name="应用名", max_length=100, unique=True)
    baseUrl = models.CharField(verbose_name="域地址", max_length=200, unique=True)
    synopsis = models.CharField(verbose_name="简介", max_length=1000, null=True)
    depart = models.ForeignKey(DepartModel, to_field="departId", related_name="apply", on_delete=models.CASCADE)

    class Meta:
        db_table = "t_apply"

    def __str__(self):
        return self.applyName

    def save(self, *args, **kwargs):
        if not self.applyId:
            self.applyId = self.get_random_number("applyId", None, None, 1000, 9999)
        super().save(*args, **kwargs)


class PortModel(BaseModel):
    portId = models.IntegerField(verbose_name="接口id", primary_key=True)
    portName = models.CharField(verbose_name="接口名", max_length=50, unique=True)
    portPath = models.CharField(verbose_name="接口地址", max_length=200, unique=True)
    synopsis = models.CharField(verbose_name="简介", max_length=1000, null=True)
    apply = models.ForeignKey(ApplyModel, to_field="applyId", related_name="port", on_delete=models.CASCADE)

    class Meta:
        db_table = "t_port"

    def __str__(self):
        return self.portPath

    def save(self, *args, **kwargs):
        if not self.portId:
            self.portId = self.get_random_number("portId", None, None, 1000, 9999)
        super().save(*args, **kwargs)
