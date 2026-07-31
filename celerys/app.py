import os
import sys
from celery import Celery
from django.conf import settings
from commons.utils.read_file import Read


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
# 创建celery实例
app = Celery('celerys')

# 读取celery配置
app.config_from_object(obj=Read('dev', 'Celery.json').get_json_file())

# 添加异常处理
try:
    app.autodiscover_tasks()


    def _patch_beat_periodic_headers():
        """确保 Beat 触发任务时带上 periodic_task_id / periodic_task_name"""
        try:
            from django_celery_beat.schedulers import ModelEntry
            _orig_init = ModelEntry.__init__

            def _init(self, model, app=None):
                _orig_init(self, model, app)
                self.options.setdefault("headers", {})
                self.options["headers"]["periodic_task_name"] = model.name
                self.options["headers"]["periodic_task_id"] = model.id

            ModelEntry.__init__ = _init
        except Exception as e:
            print(f"patch beat headers failed: {e}", file=sys.stderr)


    _patch_beat_periodic_headers()
except Exception as e:
    print(f"Error autodiscovering tasks: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
# 自动发现task
app.autodiscover_tasks()
