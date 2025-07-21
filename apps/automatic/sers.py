from rest_framework import serializers
from .models import SuitModel
from ..cases.model.interface_case import HttpCaseModel
from django.forms.models import model_to_dict
from commons.utils.getcasedata import GetCaseData


class SuitSer(serializers.ModelSerializer):

    suitId = serializers.IntegerField(read_only=True)
    caseList = serializers.PrimaryKeyRelatedField(queryset=HttpCaseModel.objects.all(), write_only=True, many=True)
    caseInfo = serializers.SerializerMethodField(method_name='_get_case_info')
    suitName = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': 'suitName不可为null',
            'blank': 'suitName不可为空字符串'
        }
    )

    class Meta:
        model = SuitModel
        fields = '__all__'

    @staticmethod
    def _get_case_info(obj):
        case_list = GetCaseData(obj).get_case("http")
        return case_list

    def validate(self, attrs):
        suit_name = attrs.get('suitName', None)
        if not suit_name:
            raise serializers.ValidationError('suitName不可为null')
        return attrs
