"""
自定义 Celery Beat 调度器
继承 django_celery_beat 的调度器，扩展自定义功能
"""
import json
from django.utils import timezone
from django_celery_beat.schedulers import DatabaseScheduler
from django_celery_beat.models import PeriodicTask
from celery import current_app
from celery.schedules import crontab, schedule
from django_celery_beat.models import (
    PeriodicTask,
    PeriodicTasks,
    IntervalSchedule,
    ClockedSchedule,
    SolarSchedule,
    CrontabSchedule
)


class CustomDatabaseScheduler(DatabaseScheduler):
    """
    自定义数据库调度器
    扩展了任务执行日志、错误处理、重试机制等功能
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_tick = None

    def setup_schedule(self):
        """设置调度计划"""
        super().setup_schedule()
        # 初始化自定义任务
        self._sync_custom_tasks()

    def _sync_custom_tasks(self):
        """同步自定义任务到 Celery Beat"""
        for task in PeriodicTask.objects.filter(enabled=True):
            try:
                self._add_custom_task(task)
            except Exception as e:
                print(f"Error syncing task {task.name}: {e}")

    def _add_custom_task(self, task):
        """添加自定义任务到调度器"""
        # 获取任务调度
        schedule_obj = self._get_task_schedule(task)
        if schedule_obj:
            # 添加到 Celery Beat
            self.app.conf.beat_schedule[task.name] = {
                'task': task.task,
                'schedule': schedule_obj,
                'args': json.loads(task.args) if task.args else (),
                'kwargs': json.loads(task.kwargs) if task.kwargs else {},
                'options': json.loads(task.options) if task.options else {},
            }

    def _get_task_schedule(self, task):
        """获取任务调度对象"""
        if task.interval:
            return task.interval.schedule
        elif task.crontab:
            return task.crontab.schedule
        elif task.solar:
            return task.solar.schedule
        elif task.clocked:
            return task.clocked.schedule
        elif task.custom_interval:
            return task.custom_interval.schedule
        elif task.custom_crontab:
            return crontab(
                minute=task.custom_crontab.minute,
                hour=task.custom_crontab.hour,
                day_of_week=task.custom_crontab.day_of_week,
                day_of_month=task.custom_crontab.day_of_month,
                month_of_year=task.custom_crontab.month_of_year,
            )
        return None

    def sync(self):
        """同步任务到数据库"""
        super().sync()
        # 同步自定义任务
        self._sync_custom_tasks()

    def apply_async(self, entry, producer=None, advance=True, **kwargs):
        """异步执行任务，并记录执行日志"""
        # 创建执行日志
        log = None
        if isinstance(entry, dict) and 'task' in entry:
            task_name = entry['task']
            try:
                custom_task = PeriodicTask.objects.get(task=task_name, enabled=True)

            except PeriodicTask.DoesNotExist:
                pass

        try:
            # 调用父类方法执行任务
            result = super().apply_async(entry, producer=producer, advance=advance, **kwargs)

            # 更新日志状态
            if log:
                log.status = 'running'
                log.save(update_fields=['status'])

            return result
        except Exception as e:
            # 记录错误
            if log:
                log.finish(
                    status='failure',
                    error_message=str(e),
                    traceback=str(e.__traceback__) if hasattr(e, '__traceback__') else None
                )
                # 更新任务失败计数
                try:
                    custom_task = PeriodicTask.objects.get(task=entry['task'])
                    custom_task.record_failure(str(e))
                except PeriodicTask.DoesNotExist:
                    pass
            raise

    def tick(self, event_t=None, min=min, **kwargs):
        """每次调度周期执行"""
        # 更新任务的下次执行时间
        self._update_next_run_times()
        return super().tick(event_t=event_t, min=min, **kwargs)

    def _update_next_run_times(self):
        """更新所有任务的下次执行时间"""
        now = timezone.now()
        for task in PeriodicTask.objects.filter(enabled=True, next_run_at__lte=now):
            try:
                task.update_next_run_time()
            except Exception as e:
                print(f"Error updating next run time for task {task.name}: {e}")

    def close(self):
        """关闭调度器"""
        super().close()

    def get_from_database(self):
        """从数据库获取任务"""
        # 获取标准任务
        tasks = super().get_from_database()

        # 添加自定义任务
        for custom_task in PeriodicTask.objects.filter(enabled=True):
            schedule_obj = self._get_task_schedule(custom_task)
            if schedule_obj:
                tasks[custom_task.name] = {
                    'task': custom_task.task,
                    'schedule': schedule_obj,
                    'args': json.loads(custom_task.args) if custom_task.args else (),
                    'kwargs': json.loads(custom_task.kwargs) if custom_task.kwargs else {},
                    'options': json.loads(custom_task.options) if custom_task.options else {},
                }

        return tasks


class TaskResultHandler:
    """任务结果处理器"""

    @staticmethod
    def handle_success(task_name, result=None):
        """处理任务成功"""
        try:
            task = PeriodicTask.objects.get(task=task_name)
            task.record_success()

        except PeriodicTask.DoesNotExist:
            pass
        except Exception as e:
            print(f"Error handling success for task {task_name}: {e}")

    @staticmethod
    def handle_failure(task_name, error_msg=None, traceback=None):
        """处理任务失败"""
        try:
            task = PeriodicTask.objects.get(task=task_name)
            task.record_failure(error_msg)

            # 更新最新的执行日志

        except PeriodicTask.DoesNotExist:
            pass
        except Exception as e:
            print(f"Error handling failure for task {task_name}: {e}")

