from django.apps import AppConfig


class CeleryTaskConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.celery_task'
