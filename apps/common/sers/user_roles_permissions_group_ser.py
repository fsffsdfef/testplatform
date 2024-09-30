from rest_framework import serializers
from ..modelss.roles_permissions_group import Permission, Role, Group
from ..models import User


class PermissionSer(serializers.ModelSerializer):
    p_id = serializers.CharField(read_only=True)

    class Meta:
        model = Permission
        fields = '__all__'


class GroupSer(serializers.ModelSerializer):
    group_id = serializers.CharField(read_only=True)

    class Meta:
        model = Group
        fields = '__all__'


class RoleSer(serializers.ModelSerializer):
    role_id = serializers.CharField(read_only=True)

    class Meta:
        model = Role
        fields = '__all__'


class UserSer(serializers.ModelSerializer):
    user_id = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = '__all__'
