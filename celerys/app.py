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
except Exception as e:
    print(f"Error autodiscovering tasks: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
# 自动发现task
app.autodiscover_tasks()
