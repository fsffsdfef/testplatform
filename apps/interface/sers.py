from apps.interface.models import *
from rest_framework import serializers


class ApplySer(serializers.ModelSerializer):
    app_id = serializers.CharField(read_only=True)

    class Meta:
        model = Apply
        fields = '__all__'


class PortSer(serializers.ModelSerializer):
    port_id = serializers.CharField(read_only=True)

    class Meta:
        model = Port
        fields = '__all__'

