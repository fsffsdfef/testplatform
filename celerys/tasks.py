import json
import uuid
import logging

from celery import shared_task
from celerys.hooks import HookTask
from apps.automatic.sers import SuitSer
from apps.automatic.models import SuitModel
from apps.cases.model.interface_case import HttpCaseModel
from commons.factory.requestFactory import RequestDispense
from commons.utils.get_case_data import GetCaseData
from commons.ws.push import push_ws

log = logging.getLogger(__name__)


def _normalize_suit_ids(suit_ids):
    """兼容 Beat args / kwargs 多种入参格式"""
    if suit_ids is None:
        return []
    if isinstance(suit_ids, int):
        return [suit_ids]
    if isinstance(suit_ids, str):
        text = suit_ids.strip()
        if not text:
            return []
        try:
            return _normalize_suit_ids(json.loads(text))
        except (json.JSONDecodeError, TypeError, ValueError):
            return [int(text)]
    if isinstance(suit_ids, (list, tuple)):
        result = []
        for item in suit_ids:
            if isinstance(item, (list, tuple)):
                result.extend(_normalize_suit_ids(item))
            elif item is not None:
                result.append(int(item))
        return result
    return []


def _calc_pass_rate(answer_list):
    assert_list = []
    for answer in answer_list:
        if not isinstance(answer, dict):
            continue
        info = answer.get('info') or []
        if isinstance(info, list):
            for item in info:
                final = item.get('assert', {}).get('finalAssert')
                if final is not None:
                    assert_list.append(bool(final))
    if not assert_list:
        return 0
    return round(sum(assert_list) / len(assert_list) * 100, 2)


def _run_single_suit(client, suit_id):
    suit_obj = SuitModel.objects.get(suitId=suit_id)
    suit_ser = SuitSer(instance=suit_obj)
    case_data = suit_ser.data['caseInfo']
    answer = client.send_request(request_type='HTTP', data=case_data)
    answer['suitID'] = suit_ser.data['suitId']
    answer['suitName'] = suit_ser.data['suitName']
    return answer


@shared_task(base=HookTask)
def SuitRequest(suit_id, task_id=None, user_id=None):
    if not task_id:
        task_id = str(uuid.uuid4())

    push_ws(task_id, user_id, {
        'type': 'start',
        'suitId': suit_id,
        'msg': '套件开始执行',
    })

    client = RequestDispense()
    try:
        answer = _run_single_suit(client, suit_id)

        push_ws(task_id, user_id, {
            'type': 'success',
            'suitId': suit_id,
            'msg': '套件执行完成',
            'data': answer,
        })
        return answer
    except Exception as e:
        log.exception('SuitRequest failed suit_id=%s', suit_id)
        push_ws(task_id, user_id, {
            'type': 'error',
            'suitId': suit_id,
            'msg': str(e),
        })
        return str(e)


@shared_task(base=HookTask)
def MultiSuitRequest(suit_ids=None, task_id=None, user_id=None, **kwargs):
    """
    多套件执行（定时任务 / 手动触发）

    Beat 配置示例：
    - task: celerys.tasks.MultiSuitRequest
    - args: [[1001, 1002, 1003]]
    或 kwargs: {"suit_ids": [1001, 1002, 1003]}
    """
    if not task_id:
        task_id = str(uuid.uuid4())

    if suit_ids is None:
        suit_ids = kwargs.get('suit_ids')

    suit_id_list = _normalize_suit_ids(suit_ids)
    if not suit_id_list:
        msg = 'suit_ids 不能为空'
        push_ws(task_id, user_id, {'type': 'error', 'msg': msg})
        return msg

    push_ws(task_id, user_id, {
        'type': 'start',
        'suitIds': suit_id_list,
        'msg': f'开始执行 {len(suit_id_list)} 个套件',
    })

    client = RequestDispense()
    suits_result = []
    errors = []

    for index, suit_id in enumerate(suit_id_list, start=1):
        try:
            answer = _run_single_suit(client, suit_id)
            suits_result.append(answer)
            push_ws(task_id, user_id, {
                'type': 'progress',
                'current': index,
                'total': len(suit_id_list),
                'suitId': suit_id,
                'msg': f'套件 {suit_id} 执行完成',
            })
        except Exception as e:
            log.exception('MultiSuitRequest failed suit_id=%s', suit_id)
            errors.append(f'套件 {suit_id}: {str(e)}')

    if not suits_result:
        msg = '; '.join(errors) if errors else '全部套件执行失败'
        push_ws(task_id, user_id, {'type': 'error', 'msg': msg})
        return msg

    result = {
        'pass': _calc_pass_rate(suits_result),
        'global': getattr(client, '_GLOBAL_MAP', {}),
        'suits': suits_result,
    }
    if errors:
        result['errors'] = errors

    push_ws(task_id, user_id, {
        'type': 'success',
        'suitIds': suit_id_list,
        'msg': '多套件执行完成',
        'data': result,
    })
    return result


@shared_task(base=HookTask)
def CaseRequest(case_id, task_id=None, user_id=None):
    if not task_id:
        task_id = str(uuid.uuid4())

    push_ws(task_id, user_id, {
        'type': 'start',
        'caseId': case_id,
        'msg': '用例开始执行',
    })

    client = RequestDispense()
    try:
        case = HttpCaseModel.objects.get(caseId=case_id)
        info = GetCaseData(case).get_case('onecase')
        answer = client.send_request(request_type='HTTP', data=info)

        push_ws(task_id, user_id, {
            'type': 'success',
            'caseId': case_id,
            'msg': '用例执行完成',
            'data': answer,
        })
        return answer
    except Exception as e:
        push_ws(task_id, user_id, {
            'type': 'error',
            'caseId': case_id,
            'msg': str(e),
        })
        return str(e)