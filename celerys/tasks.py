from apps.cases.model.interface_case import HttpCaseModel
from celerys import celery_app
from celery import shared_task
from celerys.hooks import HookTask
from apps.automatic.sers import SuitSer
from apps.automatic.models import SuitModel
from commons.factory.requestFactory import RequestDispense
from commons.cusntom.response import CustomResponse
from commons.utils.get_case_data import GetCaseData
import logging

log = logging.getLogger(__name__)


@shared_task(base=HookTask, bind=True)
def SuitRequest(data):
    log.info("执行一次")
    client = RequestDispense()
    suit_obj = SuitModel.objects.get(suitId=data)
    suit_ser = SuitSer(instance=suit_obj)
    data = suit_ser.data['caseInfo']
    suit_id = suit_ser.data['suitId']
    suit_name = suit_ser.data['suitName']
    try:
        answer = client.send_request(request_type="HTTP", data=data)
        answer['suitID'] = suit_id
        answer['suitName'] = suit_name
        return CustomResponse(data=answer, code=101)
    except Exception as e:
        return CustomResponse(data=[], code=101, msg=str(e))


# @shared_task(base=HookTask)
# def suit_action(suit_id):
#     client = RequestDispense()
#     # logger.info("日志测试", extra={'request': request.data})
#     suit_obj = SuitModel.objects.get(suitId=suit_id)
#     suit_ser = SuitSer(instance=suit_obj)
#     data = suit_ser.data['caseInfo']
#     suit_id = suit_ser.data['suitId']
#     suit_name = suit_ser.data['suitName']
#     try:
#         answer = client.send_request(request_type="HTTP", data=data)
#         answer['suitID'] = suit_id
#         answer['suitName'] = suit_name
#         return CustomResponse(data=answer, code=101)
#     except Exception as e:
#         return CustomResponse(data=[], code=101, msg=str(e))
#
#
# @shared_task(base=HookTask)
# def https_action(case_id):
#     client = RequestDispense()
#     try:
#         case = HttpCaseModel.objects.get(caseId=case_id)
#         info = GetCaseData(case).get_case("onecase")
#         answer = client.send_request(request_type="HTTP", data=info)
#         return {"data": answer}
#     except Exception as e:
#         return {'msg': str(e)}
