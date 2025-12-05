from celerys import celery_app
from celery import shared_task
from celerys.hooks import HookTask
from apps.automatic.sers import SuitSer
from apps.automatic.models import SuitModel
from commons.factory.requestFactory import RequestDispense


@shared_task(base=HookTask)
def demo(a, b):
    return f'nifdsfssddfsdfsd{a}, {b}'


@shared_task(base=HookTask)
def SuitRequest(suit_id):
    print(type(suit_id))
    client = RequestDispense()
    suit_obj = SuitModel.objects.get(suitId=suit_id)
    suit_ser = SuitSer(instance=suit_obj)
    data = suit_ser.data['caseInfo']
    answer = list()
    try:
        for case in data:
            # a = AutomatedRequest(case).http_send()
            b = client.http_request(data=case)
            answer.append(b)
        return answer
    except Exception as e:
        return {'msg': str(e)}
