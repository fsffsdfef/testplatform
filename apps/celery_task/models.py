from django.db import models
from django.utils.translation import gettext_lazy as _
from commons.abs.basemodel import BaseModel
from django.core.exceptions import MultipleObjectsReturned, ValidationError
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


class CustomClockedSchedule(BaseModel, ClockedSchedule):

    class Meta:
        db_table = "t_clocked_schedule"


class CustomCrontabSchedule(BaseModel, CrontabSchedule):
    description = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='描述',
        help_text='调度任务的描述信息'
    )
    custom_timezone = models.CharField(
        max_length=63,
        default='Asia/Shanghai',
        verbose_name='时区',
        help_text='调度时区'
    )

    class Meta:
        db_table = "t_crontab_schedule"

    def __str__(self):
        return str(self.description)


class CustomSolarSchedule(BaseModel, SolarSchedule):

    class Meta:
        db_table = "t_solar_schedule"


class CustomIntervalSchedule(BaseModel, IntervalSchedule):
    displayName = models.CharField('显示名称', max_length=200)

    class Meta:
        db_table = "t_interval"

    def __str__(self):
        return str(self.displayName)


class CustomPeriodicTask(BaseModel, PeriodicTask):
    # weekdays_only = models.BooleanField('仅工作日', default=False)
    customInterval = models.ForeignKey(
        CustomIntervalSchedule,
        null=True, blank=True, on_delete=models.CASCADE,
        related_name='task', verbose_name='自定义调度器'
    )

    customCrontab = models.ForeignKey(
        CustomCrontabSchedule, on_delete=models.CASCADE, null=True, blank=True,
        verbose_name=_('Crontab Schedule'),
        help_text=_('Crontab Schedule to run the task on.  '
                    'Set only one schedule type, leave the others null.'),
    )

    customSolar = models.ForeignKey(
        CustomSolarSchedule, on_delete=models.CASCADE, null=True, blank=True,
        verbose_name=_('Solar Schedule'),
        help_text=_('Solar Schedule to run the task on.  '
                    'Set only one schedule type, leave the others null.'),
    )
    customClocked = models.ForeignKey(
        CustomClockedSchedule, on_delete=models.CASCADE, null=True, blank=True,
        verbose_name=_('Clocked Schedule'),
        help_text=_('Clocked Schedule to run the task on.  '
                    'Set only one schedule type, leave the others null.'),
    )

    class Meta:
        db_table = "t_task"

    def validate_unique(self, *args, **kwargs):
        schedule_types = ['interval', 'crontab', 'solar', 'clocked',
                          'customInterval', 'customClocked', 'customSolar', 'customCrontab']
        selected_schedule_types = [s for s in schedule_types
                                   if getattr(self, s)]

        if len(selected_schedule_types) == 0:
            raise ValidationError(
                'One of clocked, interval, crontab, or solar '
                'must be set.'
            )

        err_msg = 'Only one of clocked, interval, crontab, ' \
                  'or solar must be set'
        if len(selected_schedule_types) > 1:
            error_info = {}
            for selected_schedule_type in selected_schedule_types:
                error_info[selected_schedule_type] = [err_msg]
            raise ValidationError(error_info)

        # clocked must be one off task
        if self.clocked and not self.one_off:
            err_msg = 'clocked must be one off, one_off must set True'
            raise ValidationError(err_msg)

