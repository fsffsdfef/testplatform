from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from itertools import chain
from ..model.user import UserModel
from ..model.depart_apply_port import DepartModel


def get_permission(obj):
    """
    获取group或role下的权限code
    @param obj: group或role实例对象
    @return: 返回权限code组
    """
    permission_list = obj.permission.all()
    return [permission.perCode for permission in permission_list]


class TokenSer(TokenObtainSerializer):

    token_class = RefreshToken

    # 获取token，并把email&用户权限塞入token中下发
    @classmethod
    def get_token(cls, user):
        permission_list = []
        group_map = map(get_permission, user.groups.all())
        role_map = map(get_permission, user.roles.all())
        per_map = chain(group_map, role_map)
        for i in per_map:
            permission_list = i + permission_list
        permission_list = list(set(permission_list))
        token = super().get_token(user)
        token['email'] = user.email
        token['permissionList'] = permission_list
        return token

    def validate(self, attrs):
        data = {}
        result = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['token'] = str(refresh.access_token)
        data['expire'] = str(refresh.access_token.payload['exp'])
        data['email'] = attrs['email']
        result['data'] = data
        return result


class UserSer(serializers.ModelSerializer):

    userId = serializers.CharField(read_only=True)
    password = serializers.CharField(write_only=True, required=False,)
    depart = serializers.PrimaryKeyRelatedField(queryset=DepartModel.objects.all())
    departName = serializers.SerializerMethodField(method_name='_get_depart_name', read_only=True)

    class Meta:
        model = UserModel
        # fields = ("userId", "password", "roles", "groups", "depart", "departName", "email",
        #           "createdDate", "updatedDate", "createUser", "updateUser"
        #           )
        fields = '__all__'
        read_only_fields = []

    @staticmethod
    def _get_depart_name(obj):
        return obj.depart.departName

    # def update(self, instance, validated_data):
    #
    #     for field, value in validated_data.items():
    #         if field in self.Meta.read_only_fields:
    #             continue
    #         setattr(instance, field, value)
    #     instance.save()
    #     return instance
