from celerys import celery_app
from celery import shared_task
from celerys.hooks import HookTask


@shared_task(base=HookTask)
def demo(a, b):
    return f'nifdsfssddfsdfsd{a}, {b}'
