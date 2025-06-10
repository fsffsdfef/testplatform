import os
from celery import Celery
from django.conf import settings
from commons.utils.readfile import Read


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
app = Celery('celerys')
app.config_from_object(obj=Read('dev', 'Celery.json').get_json_file())
app.autodiscover_tasks()