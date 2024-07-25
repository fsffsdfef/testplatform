from apps.management.models import *
from rest_framework import serializers


class DepartSer(serializers.ModelSerializer):
    depart_id = serializers.CharField(read_only=True)

    class Meta:
        model = Depart
        fields = '__all__'
