from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from ..model.user import UserModel


def get_permission(obj):
    """
    获取group或role下的权限code
    @param obj: group或role实例对象
    @return: 返回权限code组
    """
    permission_list = obj.permissions.all()
    return [permission.perCode for permission in permission_list]


class TokenSer(TokenObtainSerializer):

    token_class = RefreshToken

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        groups = user.groups.all()
        group_list = list(map(get_permission, groups))
        permission_list = []
        for i in group_list:
            permission_list = i + permission_list
        roles = user.roles.all()
        role_list = list(map(get_permission, roles))
        for i in role_list:
            permission_list = i + permission_list
        permission_list = list(set(permission_list))
        token['permissionList'] = permission_list
        return token

    def validate(self, attrs):
        data = {}
        result = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['token'] = str(refresh.access_token)
        data['expire'] = str(refresh.access_token.payload['exp'])
        result['data'] = data
        return result


class UserSer(serializers.ModelSerializer):

    class Meta:
        model = UserModel
        fields = "__all__"
