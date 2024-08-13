from rest_framework.exceptions import ValidationError

from apps.common.models import *
from rest_framework import serializers


class DepartSer(serializers.ModelSerializer):
    depart_id = serializers.CharField(read_only=True)

    class Meta:
        model = Depart
        fields = '__all__'


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


class MenuSer(serializers.ModelSerializer):
    menu_id = serializers.CharField(read_only=True)
    name = serializers.CharField(required=True, error_messages={'blank': '名称不能为空'})
    created_date = serializers.DateTimeField(read_only=True)
    updated_date = serializers.DateTimeField(read_only=True)
    extra_field = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = '__all__'

    def validate(self, attrs):
        data = self.initial_data.get('menu_id', None)
        name = attrs.get('name', None)
        if data:
            return attrs
        try:
            queryset = self.Meta.model.objects.get(name=name)
            if queryset:
                raise ValidationError('菜单名不可重复')
        except Menu.DoesNotExist as e:
            print(e)
        return attrs

    def create(self, validated_data):
        instance = self.Meta.model.objects.create(**validated_data)
        return instance

    def update(self, instance, validated_data):
        instance.menu_id = validated_data.get('menu_id', instance.menu_id)
        instance.name = validated_data.get('name', instance.name)
        instance.parent = validated_data.get('parent', instance.parent)
        instance.create_user = validated_data.get('create_user', instance.create_user)
        instance.update_user = validated_data.get('update_user', instance.update_user)
        instance.save()
        return instance

    def save(self, **kwargs):
        model_date = {key: value for key, value in self.validated_data.items() if key in self.Meta.fields}
        extra_date = {key: value for key, value in self.validated_data.items() if key not in self.Meta.fields}

        instance = super().save(**model_date)
        return instance

    def to_representation(self, instance):
        instance.extra_field = instance
        ret = super().to_representation(instance)
        return ret

    def get_extra_field(self, obj):
        pass


