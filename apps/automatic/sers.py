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

    @staticmethod
    def _create_suit_case(suit, case_info):
        case_id = case_info.get('caseId')
        try:
            case = HttpCaseModel.objects.get(caseId=case_id)
        except HttpCaseModel.DoesNotExist:
            raise serializers.ValidationError(f"用例ID {case_id} 不存在")

        return SuitCaseModel.objects.create(
            suit=suit,
            case=case,
            execution_order=case_info.get('execution_order'),
            globalMap=case_info.get('globalMap'),
            streamKey=case_info.get('streamKey'),
            is_first=case_info.get('is_first', False),
            is_last=case_info.get('is_last', False),
            is_stream=case_info.get('is_stream', False),
            changeSid=case_info.get('changeSid', False),
            changeSidKey=case_info.get('changeSidKey'),
        )

    def create(self, validated_data):
        case_list = validated_data.pop('casesList', [])
        with transaction.atomic():
            suit = SuitModel.objects.create(**validated_data)
            for case_info in case_list:
                self._create_suit_case(suit, case_info)
        return suit

    def update(self, instance, validated_data):
        case_list = validated_data.pop('casesList', None)
        with transaction.atomic():
            suit = super().update(instance, validated_data)
            if case_list is not None:
                SuitCaseModel.objects.filter(suit=instance).delete()
                for case_info in case_list:
                    self._create_suit_case(suit, case_info)
        return suit
