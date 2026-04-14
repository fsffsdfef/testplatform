from django.db import models
from django_celery_beat.models import PeriodicTask


class CustomSchedule(models.Model):
    """
    自定义调度配置表
    扩展 django-celery-beat 的 PeriodicTask
    """
    periodic_task = models.OneToOneField(
        PeriodicTask,
        on_delete=models.CASCADE,
        related_name='custom_schedule'
    )

    # 自定义字段
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    priority = models.IntegerField(default=5, verbose_name="任务优先级")
    max_retries = models.IntegerField(default=3, verbose_name="最大重试次数")
    retry_delay = models.IntegerField(default=60, verbose_name="重试延迟(秒)")

    # 动态条件字段
    condition_field = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="条件字段名"
    )
    condition_value = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="条件值"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 't_custom_schedule'
        verbose_name = '自定义调度配置'
        verbose_name_plural = '自定义调度配置'
