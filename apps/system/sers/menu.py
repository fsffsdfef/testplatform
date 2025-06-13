from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from ..model.meu import Menu
from ..model.permission_group_role import PermissionModel


class MenuSer(serializers.ModelSerializer):
    menuId = serializers.IntegerField(read_only=True)
    menuName = serializers.CharField(required=True, error_messages={'blank': '名称不能为空'})
    permissionList = serializers.SerializerMethodField(method_name='get_permission_list', read_only=True)
    previousMenu = serializers.SerializerMethodField(method_name='get_previous_menu')
    per = serializers.PrimaryKeyRelatedField(many=True, queryset=PermissionModel.objects.all(), write_only=True)

    class Meta:
        model = Menu
        fields = '__all__'
        # exclude = ['createdDate', 'updatedDate', 'createUser', 'updateUser']

    @staticmethod
    def get_permission_list(obj):
        permission_list = obj.per.all()
        return [permission.perCode for permission in permission_list]

    @staticmethod
    def get_previous_menu(obj):
        if obj.parent is not None:
            return obj.parent.menuName
        return None

    def validate(self, attrs):
        # data = self.initial_data.get('menuId', None)
        # name = attrs.get('menuName', None)
        # if data:
        #     return attrs
        # try:
        #     queryset = self.Meta.model.objects.get(menuName=name)
        #     if queryset:
        #         raise ValidationError('菜单名不可重复')
        # except Menu.DoesNotExist as e:
        #     print(e)
        return attrs
