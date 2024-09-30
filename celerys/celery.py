import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testplatform.settings')
django.setup()
from celery import Celery
from utils.read import ReadFile

app = Celery('celerys')

# 读取celery配置文件
celery_config = ReadFile('json', 'celeryconfig.json').distinguish()
app.config_from_object(obj=celery_config)

from django_celery_beat.schedulers import DatabaseScheduler
