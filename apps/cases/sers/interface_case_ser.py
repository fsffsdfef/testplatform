from rest_framework import serializers
from django.db import transaction
from ..model.interface_case import *
from ..sers.express_ser import *
from commons.utils.get_case_data import GetCaseData
from apps.automatic.models import SuitCaseModel


class HttpCaseSer(serializers.ModelSerializer):
    caseId = serializers.CharField(read_only=True)
    expressItem = ExpressItemSer(many=True)
    portName = serializers.SerializerMethodField(method_name='_get_port_name')

    class Meta:
        model = HttpCaseModel
        fields = '__all__'

    def create(self, validated_data):
        express_items = validated_data.pop('expressItem', [])
        instance = super().create(validated_data)
        for express_item in express_items:
            express_data = express_item.pop('expressList', [])
            express_item = ExpressItem.objects.create(httpCase=instance, **express_item)
            for express in express_data:
                Expresses.objects.create(expressItem=express_item, **express)
        return instance

    def update(self, instance, validated_data):
        express_items = validated_data.pop('expressItem')
        with transaction.atomic():
            for field, value in validated_data.items():
                if value is not None:
                    setattr(instance, field, value)
            # for field, value in validated_data.items():
            #     setattr(instance, field, value)
            instance.save()
            if express_items:
                self._update_express_items(instance, express_items)
            return instance

    def _update_express_items(self, instance, items_data):
        """更新表达式项 - 保持ID不变，只新增没有ID的"""

        # 获取所有传入的ID
        incoming_item_ids = [item.get('expressItemId') for item in items_data if item.get('expressItemId')]
        # 获取当前case下关联的规则id
        history_express_ids = list(instance.expressItem.all().values_list('expressItemId', flat=True))
        # 获取与传入的id不同的id作为删除项并删除
        removed = set(history_express_ids) - set(incoming_item_ids)
        if removed:
            instance.expressItem.filter(expressItemId__in=removed).delete()

        # 更新每个expressItem
        for item_data in items_data:
            express_item_id = item_data.get('expressItemId')
            express_list = item_data.pop('expressList', [])

            if express_item_id:
                # 判断是否是现有数据，不是则新增
                express_item, created = ExpressItem.objects.get_or_create(
                    expressItemId=express_item_id,
                    httpCase=instance,
                    defaults=item_data
                )

                if not created:
                    # 更新现有项
                    for field, value in item_data.items():
                        if value is not None:
                            setattr(express_item, field, value)
                    express_item.save()

                # 处理表达式
                self._handle_expresses(express_item, express_list)
            else:
                # 创建新项
                express_item = ExpressItem.objects.create(httpCase=instance, **item_data)
                self._handle_expresses(express_item, express_list)

    @staticmethod
    def _handle_expresses(express_item, express_list):
        """处理表达式列表"""
        # 获取所有传入的表达式ID
        incoming_express_ids = [exp.get('expressId') for exp in express_list if exp.get('expressId')]
        history_express_ids = list(express_item.expressList.all().values_list('expressId', flat=True))
        removed = set(history_express_ids) - set(incoming_express_ids)
        if removed:
            express_item.expressList.filter(expressId__in=removed).delete()
        # 处理每个表达式
        for express_data in express_list:
            express_id = express_data.get('expressId')

            if express_id:
                # 更新现有表达式
                express, created = Expresses.objects.get_or_create(
                    expressId=express_id,
                    expressItem=express_item,
                    defaults=express_data
                )

                if not created:
                    # 更新现有表达式
                    for field, value in express_data.items():
                        if value is not None:
                            setattr(express, field, value)
                    express.save()
            else:
                # 创建新表达式
                Expresses.objects.create(expressItem=express_item, **express_data)

    @staticmethod
    def _create_express_item(instance, express_item_data):
        for express_item in express_item_data:
            express_data = express_item.pop('expressList', [])
            express_item = ExpressItem.objects.create(httpCase=instance, **express_item)
            for express in express_data:
                Expresses.objects.create(expressItem=express_item, **express)

    @staticmethod
    def _get_port_name(obj):
        return obj.port.portName

    def validate(self, attrs):
        return attrs


class SuitCaseSerializer(serializers.ModelSerializer):
    """套件用例关联序列化器"""

    case_id = serializers.IntegerField(write_only=True)
    case = serializers.SerializerMethodField(method_name='_get_case_info')
    items = serializers.SerializerMethodField(method_name="_get_items")

    class Meta:
        model = SuitCaseModel
        fields = ['id', 'case', 'case_id', 'execution_order', 'is_first', 'is_last', 'changeSidKey', 'changeSid',
                  'globalMap', 'created_at', 'updated_at', 'streamKey', 'items']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        case_id = validated_data.pop('caseId')
        try:
            case = HttpCaseModel.objects.get(caseId=case_id)
        except HttpCaseModel.DoesNotExist:
            raise serializers.ValidationError(f"用例ID {case_id} 不存在")

        validated_data['case'] = case
        return super().create(validated_data)

    @staticmethod
    def _get_case_info(obj):
        case = GetCaseData(obj).get_case("httpObj")
        return case

    @staticmethod
    def _get_items(obj):
        global_map = obj.globalMap
        if global_map and len(global_map) >= 1:
            items = []
            for k, v in global_map.items():
                _ = dict()
                _["key"] = k
                _["value"] = v
                items.append(_)
            return items
        else:
            return []

