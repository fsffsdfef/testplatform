from django.db import models
from commons.abs.basemodel import BaseModel
from .depart_apply_port import DepartModel


class PermissionModel(BaseModel):
    perId = models.AutoField(primary_key=True)
    perCode = models.CharField(verbose_name="权限code", max_length=200)
    synopsis = models.CharField(verbose_name="简介", max_length=1000, null=True)

    class Meta:
        db_table = "t_permission"

    def __str__(self):
        return self.perCode


class GroupModel(BaseModel):
    groupId = models.AutoField(primary_key=True)
    groupName = models.CharField(verbose_name="组名称", max_length=200)
    synopsis = models.CharField(verbose_name="简介", max_length=1000, null=True)
    permission = models.ManyToManyField(PermissionModel, related_name="group", blank=True)
    depart = models.ForeignKey(DepartModel, to_field="departId", on_delete=models.CASCADE)

    class Meta:
        db_table = "t_group"

    def __str__(self):
        return self.groupName


class RoleModel(BaseModel):
    roleId = models.AutoField(primary_key=True)
    roleName = models.CharField(verbose_name="角色名", max_length=200)
    synopsis = models.CharField(verbose_name="简介", max_length=1000, null=True)
    permission = models.ManyToManyField(PermissionModel, related_name="role", blank=True)

    class Meta:
        db_table = "t_role"

    def __str__(self):
        return self.roleName
