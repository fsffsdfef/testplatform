from django.db import models
from django.utils import timezone
import json


class LogEntry(models.Model):
    """日志条目模型"""
    LEVEL_CHOICES = [
        ('DEBUG', 'DEBUG'),
        ('INFO', 'INFO'),
        ('WARNING', 'WARNING'),
        ('ERROR', 'ERROR'),
        ('CRITICAL', 'CRITICAL'),
    ]

    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, db_index=True)
    logger_name = models.CharField(max_length=100, db_index=True)
    message = models.TextField()
    module = models.CharField(max_length=100, blank=True, null=True)
    func_name = models.CharField(max_length=100, blank=True, null=True)
    line_no = models.IntegerField(blank=True, null=True)
    thread = models.CharField(max_length=50, blank=True, null=True)
    process = models.CharField(max_length=50, blank=True, null=True)
    extra_data = models.JSONField(default=dict, blank=True, null=True)
    exception_info = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'log_entry'
        verbose_name = '日志条目'
        verbose_name_plural = '日志条目'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at', 'level']),
            models.Index(fields=['logger_name', '-created_at']),
            models.Index(fields=['level', '-created_at']),
        ]

    def __str__(self):
        return f"[{self.level}] {self.logger_name} - {self.message[:50]}"

    @classmethod
    def cleanup_old_logs(cls, days=30):
        """清理旧日志"""
        from django.utils import timezone
        from datetime import timedelta
        cutoff_date = timezone.now() - timedelta(days=days)
        return cls.objects.filter(created_at__lt=cutoff_date).delete()