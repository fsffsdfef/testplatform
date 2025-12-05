import os
from celery import Celery
from django.conf import settings
from commons.utils.readfile import Read


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
# 创建celery实例
app = Celery('celerys')

# 读取celery配置
app.config_from_object(obj=Read('dev', 'Celery.json').get_json_file())
# 自动发现task
app.autodiscover_tasks()
