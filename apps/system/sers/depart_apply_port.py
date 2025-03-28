from rest_framework import serializers
from ..model.depart_apply_port import *


class ApplySer(serializers.ModelSerializer):

    class Meta:
        model = ApplyModel
        fields = "__all__"


class PortSer(serializers.ModelSerializer):

    class Meta:
        model = PortModel
        fields = "__all__"


class DepartSer(serializers.ModelSerializer):

    apply = ApplySer(many=True, read_only=True)

    class Meta:
        model = DepartModel
        fields = "__all__"

    def validate(self, attrs):
        return attrs

