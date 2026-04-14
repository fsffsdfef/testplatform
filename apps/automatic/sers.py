from rest_framework import serializers
from .models import SuitModel, SuitCaseModel
from ..cases.model.interface_case import HttpCaseModel
from ..cases.sers.interface_case_ser import SuitCaseSerializer
from django.forms.models import model_to_dict
from commons.utils.get_case_data import GetCaseData
from django.db import transaction


class SuitSer(serializers.ModelSerializer):

    suitId = serializers.IntegerField(read_only=True)
    # caseList = serializers.PrimaryKeyRelatedField(queryset=HttpCaseModel.objects.all(), write_only=True, many=True)
    caseInfo = SuitCaseSerializer(source='suitcasemodel_set', many=True, read_only=True)
    # caseInfo = serializers.SerializerMethodField(method_name='_get_case_info')
    caseSize = serializers.SerializerMethodField(method_name="_get_case_size")
    selectList = serializers.SerializerMethodField(method_name="_get_select_list")
    suitName = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'suitName不可为null',
            'blank': 'suitName不可为空字符串'
        }
    )
    casesList = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False,
        help_text="用例列表，格式: [{'case_id': 1, 'execution_order': 1, 'is_first': False, 'is_last': False}]"
    )

    class Meta:
        model = SuitModel
        fields = '__all__'

    # @staticmethod
    # def _get_case_info(obj):
    #     case_list = GetCaseData(obj).get_case("http")
    #     return case_list

    @staticmethod
    def _get_case_size(obj):
        return int(obj.casesList.count())

    @staticmethod
    def _get_select_list(obj):
        select_list = list()
        for i in obj.suitcasemodel_set.all():
            case_list = list()
            case_id = i.case.caseId
            port_id = i.case.port.portId
            apply_id = i.case.port.apply.applyId
            depart_id = i.case.port.apply.depart.departId
            case_list.append(depart_id)
            case_list.append(apply_id)
            case_list.append(port_id)
            case_list.append(case_id)
            select_list.append(case_list)
        return select_list

    def validate(self, attrs):
        """入参校验"""
        return attrs

    def create(self, validated_data):
        case_list = validated_data.pop("casesList", [])
        # 使用事务确保数据一致性
        with transaction.atomic():
            # 创建套件
            suit = SuitModel.objects.create(**validated_data)
            # 创建关联关系
            for case_info in case_list:
                case_id = case_info.get('caseId')
                execution_order = case_info.get('execution_order')
                global_map = case_info.get('globalMap')
                stream_key = case_info.get('streamKey')
                is_first = case_info.get('is_first', False)
                is_last = case_info.get('is_last', False)

                try:
                    case = HttpCaseModel.objects.get(caseId=case_id)
                    SuitCaseModel.objects.create(
                        suit=suit,
                        case=case,
                        execution_order=execution_order,
                        globalMap=global_map,
                        is_first=is_first,
                        is_last=is_last,
                        streamKey=stream_key
                    )
                except HttpCaseModel.DoesNotExist:
                    # 可以选择抛出异常或跳过
                    raise serializers.ValidationError(f"用例ID {case_id} 不存在")

        return suit

    def update(self, instance, validated_data):
        case_list = validated_data.pop('casesList', None)

        with transaction.atomic():
            # 更新套件基本信息
            suit = super().update(instance, validated_data)

            # 如果提供了case_list，则更新用例列表
            if case_list is not None:
                # 清空现有用例关联
                SuitCaseModel.objects.filter(suit=instance).delete()

                # 创建新的关联关系
                for case_info in case_list:
                    case_id = case_info.get('caseId')
                    execution_order = case_info.get('execution_order')
                    is_first = case_info.get('is_first', False)
                    is_last = case_info.get('is_last', False)

                    try:
                        case = HttpCaseModel.objects.get(caseId=case_id)
                        SuitCaseModel.objects.create(
                            suit=suit,
                            case=case,
                            execution_order=execution_order,
                            is_first=is_first,
                            is_last=is_last
                        )
                    except HttpCaseModel.DoesNotExist:
                        raise serializers.ValidationError(f"用例ID {case_id} 不存在")

        return suit
