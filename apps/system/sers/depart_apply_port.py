from rest_framework import serializers
from ..model.depart_apply_port import *
from ..model.permission_group_role import *
from apps.cases.sers.interface_case_ser import HttpCaseSer


class ApplySer(serializers.ModelSerializer):
    applyId = serializers.IntegerField(read_only=True)

    class Meta:
        model = ApplyModel
        fields = "__all__"


class PortSer(serializers.ModelSerializer):
    portId = serializers.CharField(read_only=True)
    case = HttpCaseSer(many=True, read_only=True)

    class Meta:
        model = PortModel
        fields = "__all__"


class DepartSer(serializers.ModelSerializer):

    apply = ApplySer(many=True, read_only=True)
    departId = serializers.CharField(read_only=True)

    class Meta:
        model = DepartModel
        fields = "__all__"

    def validate(self, attrs):
        return attrs


class PerSer(serializers.ModelSerializer):

    class Meta:
        model = PermissionModel
        fields = "__all__"


class RoleSer(serializers.ModelSerializer):

    class Meta:
        model = RoleModel
        fields = "__all__"


class GroupSer(serializers.ModelSerializer):

    class Meta:
        model = GroupModel
        fields = "__all__"
