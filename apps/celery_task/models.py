from django.db import models
from django.utils.translation import gettext_lazy as _
from commons.abs.basemodel import BaseModel
from django_celery_beat.models import (
    PeriodicTask,
    PeriodicTasks,
    IntervalSchedule,
    ClockedSchedule,
    SolarSchedule,
    CrontabSchedule
)
from apps.system.model.depart_apply_port import ApplyModel
import json
# Create your models here.


class CustomIntervalSchedule(BaseModel, IntervalSchedule):
    displayName = models.CharField('显示名称', max_length=200)

    class Meta:
        db_table = "t_interval"

    def __str__(self):
        return str(self.displayName)


class CustomPeriodicTask(BaseModel, PeriodicTask):
    customInterval = models.ForeignKey(
        CustomIntervalSchedule,
        null=True, blank=True, on_delete=models.CASCADE,
        related_name='task', verbose_name='自定义调度器'
    )

    class Meta:
        db_table = "t_task"