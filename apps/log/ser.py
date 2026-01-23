from .models import LogEntry
from rest_framework.serializers import ModelSerializer


class LogEntrySer(ModelSerializer):

    class Meta:
        model = LogEntry
        fields = "__all__"
