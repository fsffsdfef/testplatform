from django.db import IntegrityError
from django.db import connection
from rest_framework import serializers
from ..model.test import *

MAX_BATCH_SIZE = 100


class BulkCreateSerializer(serializers.ListSerializer):
    EXISTING_IDS = set()

    def __init__(self, key, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.EXISTING_IDS = set(self.child.Meta.model.objects.values_list(key, flat=True))

    def validate(self, attrs):
        if len(attrs) > MAX_BATCH_SIZE:
            raise serializers.ValidationError(f'单次操作最多允许{MAX_BATCH_SIZE}条')
        return super().validate(attrs)

    def create(self, validated_data):
        model_class = self.child.Meta.model
        instance_list = [model_class(**item) for item in validated_data]
        try:
            # ✅ 显式调用bulk_create
            created_instances = model_class.objects.bulk_create(instance_list)
            # 补充自增ID（MySQL等需要）
            # if model_class._meta.auto_field:
            #     first_id = created_instances[0].pk
            #     for i, instance in enumerate(created_instances):
            #         instance.pk = first_id + i
            return created_instances
        except IntegrityError as e:
            raise serializers.ValidationError(f"数据冲突: {str(e)}")


class OneModelSer(serializers.ModelSerializer):

    class Meta:
        model = OneModel
        fields = '__all__'
        list_serializer_class = BulkCreateSerializer


class TwoModelSer(serializers.ModelSerializer):

    class Meta:
        model = TwoModel
        fields = '__all__'


class ThreeModelSer(serializers.ModelSerializer):

    class Meta:
        model = ThreeModel
        fields = '__all__'
