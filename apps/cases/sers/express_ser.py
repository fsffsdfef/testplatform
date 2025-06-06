from ..model.express import *
from rest_framework import serializers


class ExpressSer(serializers.ModelSerializer):
    expressId = serializers.IntegerField(required=False)

    class Meta:
        model = Expresses
        # fields = '__all__'
        exclude = ['expressItem', 'createdDate', 'updatedDate', 'createUser', 'updateUser']


class ExpressItemSer(serializers.ModelSerializer):
    expressItemId = serializers.IntegerField(required=False)
    expressList = ExpressSer(many=True)

    class Meta:
        model = ExpressItem
        # fields = '__all__'
        exclude = ['updateUser', 'createUser', 'httpCase']

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

