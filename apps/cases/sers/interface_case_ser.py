from rest_framework import serializers
from django.db import transaction
from ..model.interface_case import *
from ..sers.express_ser import *


class HttpCaseSer(serializers.ModelSerializer):
    caseId = serializers.IntegerField(read_only=True)
    expressItem = ExpressItemSer(many=True)

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
            instance.caseName = validated_data.get('caseName', instance.caseName)
            instance.headers = validated_data.get('headers', instance.headers)
            instance.body = validated_data.get('body', instance.body)
            instance.timeOut = validated_data.get('timeOut', instance.timeOut)
            instance.retries = validated_data.get('retries', instance.retries)
            instance.isCore = validated_data.get('isCore', instance.isCore)
            instance.port = validated_data.get('port', instance.port)
            instance.save()
            if express_items:
                self._update_express_items(instance, express_items)
            return instance

    @staticmethod
    def _update_express_items(instance, items_data):
        for item_data in items_data:
            express_item = item_data.pop('expressList')
            for express in express_item:
                express_id = express.get('expressId')
                express_obj = Expresses.objects.get(pk=express_id)
                ser = ExpressSer(instance=express_obj, data=express)
                if ser.is_valid(raise_exception=True):
                    ser.save()

    def validate(self, attrs):
        return attrs

