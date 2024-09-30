from apps.automation.models.interface import Apply
from apps.common.sers.departser import ApplySer
import json


class GetCases:
    def __init__(self, task_type):
        self.task_type = task_type

    def get_suite_case(self, suite: str):
        pass

    @staticmethod
    def get_apply_case(apply: str) -> list:
        data = Apply.objects.filter(appId=apply)
        ser = ApplySer(instance=data, many=True)
        # case_list = json.dumps(ser.data, ensure_ascii=True)
        # return json.loads(case_list)
        return ser.data


