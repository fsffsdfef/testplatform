from celerys import celery_app


@celery_app.task
def task_demo():
    return '任务运行了00012次'


@celery_app.task
def task_demo1():
    return '任务运行了1次'


@celery_app.task
def task_demo2():
    return '任务运行了2次'
