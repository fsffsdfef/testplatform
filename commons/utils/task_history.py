import logging
from datetime import datetime

from django.core.cache import cache
from django_celery_beat.models import PeriodicTask

log = logging.getLogger(__name__)

HISTORY_SIZE = 10
CACHE_PREFIX = 'periodic_task_history:'
CACHE_TIMEOUT = 60 * 60 * 24 * 30  # 30天


def _cache_key(periodic_task_id):
    return f'{CACHE_PREFIX}{int(periodic_task_id)}'


def _resolve_periodic_task(request, kwargs=None):
    kwargs = kwargs or {}
    headers = getattr(request, 'headers', None) or {}

    periodic_id = (
        kwargs.get('periodic_task_id')
        or headers.get('periodic_task_id')
        or getattr(request, 'periodic_task_id', None)
    )
    if periodic_id:
        pt = PeriodicTask.objects.filter(id=periodic_id).first()
        if pt:
            return pt

    periodic_name = (
        headers.get('periodic_task_name')
        or getattr(request, 'periodic_task_name', None)
    )
    if periodic_name:
        return PeriodicTask.objects.filter(name=periodic_name).first()

    return None


def append_periodic_task_history(request, status, retval, task_id, kwargs=None):
    pt = _resolve_periodic_task(request, kwargs)
    if not pt:
        log.warning(
            '未识别到定时任务，跳过写入运行历史 task_id=%s headers=%s kwargs=%s',
            task_id,
            getattr(request, 'headers', None),
            kwargs,
        )
        return

    is_success = status in ('SUCCESS', 'success')

    # 成功时保存 dict（单套件 / 多套件 suits 结构）
    data = None
    if is_success and isinstance(retval, dict):
        data = retval
    elif is_success and isinstance(retval, list):
        # 兼容极端情况
        data = {'suits': retval}

    record = {
        'runAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'status': 'success' if is_success else 'failure',
        'taskId': task_id,
        'msg': '' if is_success else str(retval),
        'data': data,
    }

    key = _cache_key(pt.id)
    history = cache.get(key) or []
    history.insert(0, record)
    cache.set(key, history[:HISTORY_SIZE], timeout=CACHE_TIMEOUT)
    log.info('写入定时任务运行历史 periodic_task_id=%s count=%s', pt.id, len(history))


def get_periodic_task_history(periodic_task_id):
    return cache.get(_cache_key(periodic_task_id)) or []