from celerys import celery_app
from utils.reuqest.getcase import GetCases


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
    if task_type == 'apply_case':
        case_info = GetCases(task_type).get_apply_case(id)
        return case_info
    elif task_type == 'suit_case':
        pass
    else:
        return {'code': 801, 'msg': '未识别请求类型'}
