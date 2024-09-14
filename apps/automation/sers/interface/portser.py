from rest_framework import serializers
from apps.automation.models.interface import Port
from apps.automation.sers.interface.httpser import InterfaceHttpSer


class PortSer(serializers.ModelSerializer):
    httpCase = InterfaceHttpSer(many=True, read_only=True)

    class Meta:
        model = Port
        fields = '__all__'
        