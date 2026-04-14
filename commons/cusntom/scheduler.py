from celery import current_app
from django_celery_beat.schedulers import DatabaseScheduler
from django.core.cache import cache
from django.utils.timezone import now
from apps.celery_task.models import CustomSchedule
import logging

logger = logging.getLogger(__name__)


class CustomDatabaseScheduler(DatabaseScheduler):
    """
    自定义数据库调度器
    基于 CustomSchedule 表进行任务调度
    """
    
    Model = CustomSchedule  # 使用自定义模型
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_update = now()
        self._schedule_cache_key = 'celery:custom_schedule:cache'
        self._cache_timeout = 30  # 缓存30秒
        
    def get_schedule(self):
        """
        获取调度计划
        """
        schedule = {}
        
        try:
            # 检查缓存
            cached = cache.get(self._schedule_cache_key)
            if cached:
                return cached
            
            # 查询激活的自定义调度任务
            custom_schedules = CustomSchedule.objects.filter(
                is_active=True,
                periodic_task__enabled=True
            ).select_related('periodic_task')
            
            for custom_schedule in custom_schedules:
                task_name = custom_schedule.periodic_task.task
                
                # 检查条件字段（可选）
                if (custom_schedule.condition_field and 
                    custom_schedule.condition_value):
                    if not self._check_condition(
                        custom_schedule.condition_field,
                        custom_schedule.condition_value
                    ):
                        continue
                
                # 创建调度条目
                schedule_entry = {
                    'task': task_name,
                    'schedule': custom_schedule.periodic_task.interval,
                    'args': custom_schedule.periodic_task.args or (),
                    'kwargs': custom_schedule.periodic_task.kwargs or {},
                    'options': {
                        'expires': custom_schedule.periodic_task.expires,
                        'queue': custom_schedule.periodic_task.queue,
                        'priority': custom_schedule.priority,
                        'max_retries': custom_schedule.max_retries,
                        'retry_delay': custom_schedule.retry_delay,
                    }
                }
                
                schedule[task_name] = schedule_entry
            
            # 缓存结果
            cache.set(
                self._schedule_cache_key, 
                schedule, 
                self._cache_timeout
            )
            
        except Exception as e:
            logger.error(f"获取自定义调度失败: {e}")
        
        return schedule
    
    def _check_condition(self, field_name, expected_value):
        """
        检查动态条件是否满足
        可根据业务需求自定义条件检查逻辑
        """
        try:
            # 示例：检查配置表中的某个状态
            from django.apps import apps
            
            # 这里只是示例，实际实现需根据具体业务
            # 例如：检查用户数是否达到阈值
            # 检查某个表的数据状态等
            
            return True  # 简化示例
            
        except Exception as e:
            logger.error(f"条件检查失败: {e}")
            return False
    
    def setup_schedule(self):
        """
        初始化调度器
        """
        super().setup_schedule()
        
        # 自定义初始化逻辑
        self._cleanup_old_tasks()
    
    def _cleanup_old_tasks(self):
        """
        清理旧任务（可选）
        """
        try:
            from django_celery_results.models import TaskResult
            
            # 删除超过30天的任务结果
            from datetime import timedelta
            from django.utils.timezone import now
            
            cutoff_date = now() - timedelta(days=30)
            TaskResult.objects.filter(
                date_done__lt=cutoff_date
            ).delete()
            
        except Exception as e:
            logger.error(f"清理旧任务失败: {e}")