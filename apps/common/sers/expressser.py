from apps.common.models import Expresses, ExpressItem
from rest_framework import serializers


class ExpressesSer(serializers.ModelSerializer):
    expressId = serializers.CharField(read_only=True)
    expressItem = serializers.CharField(required=False)

    class Meta:
        model = Expresses
        fields = '__all__'


class ExpressItemSer(serializers.ModelSerializer):
    expressItemId = serializers.CharField(read_only=True)
    expressList = ExpressesSer(many=True)
    httpCase = serializers.CharField(required=False)

    class Meta:
        model = ExpressItem
        fields = '__all__'

    def create(self, validated_data):
        express_data = validated_data.pop('expressList', [])
        expressitem = self.Meta.model.objects.create(**validated_data)
        for express in express_data:
            Expresses.objects.create(expressItem=expressitem, **express)
        return expressitem





