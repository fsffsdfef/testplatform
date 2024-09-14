from apps.automation.models.interface import *
from apps.common.sers.expressser import ExpressItemSer
from rest_framework import serializers


class InterfaceHttpSer(serializers.ModelSerializer):
    caseId = serializers.CharField(read_only=True)
    expressItem = ExpressItemSer(many=True)

    class Meta:
        model = InterfaceHttpCases
        fields = '__all__'

    def create(self, validated_data):
        express_items = validated_data.pop('expressItem', [])
        instance = self.Meta.model.objects.create(**validated_data)
        for express_item in express_items:
            express_data = express_item.pop('expressList', [])
            expressItem = ExpressItem.objects.create(httpCase=instance, **express_item)
            for express in express_data:
                Expresses.objects.create(expressItem=expressItem, **express)
        return instance

    # def update(self, instance, validated_data):
    #     instance.caseId = validated_data.get('caseId', instance.caseId)
    #     instance.caseName = validated_data.get('caseName', instance.caseName)
    #     instance.headers = validated_data.get('headers', instance.headers)
    #     instance.body = validated_data.get('body', instance.body)
    #     instance.timeOut = validated_data.get('timeOut', instance.timeOut)
    #     instance.retries = validated_data.get('retries', instance.retries)
    #     express_items = validated_data.pop('expressItem', [])
    #     for expressItem in express_items:
    #         expressItemId = expressItem.get('expressItemId', None)
    #         ser = ExpressItemSer(expressItemId, data=expressItem)
    #         if ser.is_valid():
    #             ser.save()
    #     instance.save()
    #     return instance

