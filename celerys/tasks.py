import json
from celerys import celery_app
from utils.reuqest.getcase import GetCases
from utils.reuqest.send_request import RequestUtil


@celery_app.task
def task_demo():
    return '任务运行了00012次'


@celery_app.task
def task_demo1():
    return '任务运行了1次'


@celery_app.task
def task_demo2():
    return '任务运行了2次'


@celery_app.task
def interface_automation_task(task_type: str, id: str):
    res_list = []
    if task_type == 'apply_case':
        apply_case_info = GetCases(task_type).get_apply_case(id)
        for apply_cases in apply_case_info:
            domains = apply_cases.pop('domains', None)
            port_cases_list = apply_cases.pop('port', None)
            for port_cases in port_cases_list:
                method = port_cases.pop('portMethod', None)
                port_name = port_cases.pop('portName', None)
                case_list = port_cases.pop('httpCase', None)
                results = map(RequestUtil(method=method, url=domains+port_name).send, case_list)
                res_list.append(list(results))
        return res_list
    elif task_type == 'suit_case':
        pass
    else:
        return {'code': 801, 'msg': '未识别请求类型'}


