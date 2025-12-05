from django.db import models
from django.utils import timezone
# Create your models here.


class LogEntry(models.Model):
    LEVEL_CHOICES = (
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    )

    logger_name = models.CharField(max_length=100)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    trace = models.TextField(blank=True, null=True)  # 存储堆栈跟踪

    def __str__(self):
        return f"{self.created_at} - {self.level} - {self.message[:50]}"

    class Meta:
        db_table = "t_log"


