from celery import Task


class HookTask(Task):

    def before_start(self, task_id, args, kwargs):
        print(f"开始执行异步任务之前，{task_id}, {args}")
        return super().before_start(task_id, args, kwargs)

    def on_success(self, retval, task_id, args, kwargs):
        print(f"执行完成了{retval}, {task_id}, {args}, {kwargs}")
        super().on_success(retval, task_id, args, kwargs)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        print(f"执行后，{status}，{retval}, {task_id}, {args}, {kwargs}, {einfo}")
        super().after_return(status, retval, task_id, args, kwargs, einfo)


