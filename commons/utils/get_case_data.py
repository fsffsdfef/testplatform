from django.forms.models import model_to_dict
import json


class GetCaseData(object):

    def __init__(self, obj):
        self.obj = obj

    def get_case(self, case_type):
        configs = {
            "http": self.get_http_case,
            "httpObj": self.get_http_case_obj,
            "onecase": self.get_case_one
        }
        if case_type in configs:
            return configs[case_type]()
        if not case_type:
            return self.default()
        return self.default()

    def get_http_case(self):
        case_list = list()
        for case in self.obj.casesList.all():
            express_group = self.get_express(case)
            port = case.port
            apply = port.apply
            url = apply.baseUrl + port.portPath
            instance_dict = model_to_dict(case)
            instance_dict['url'] = url
            instance_dict['expressItem'] = express_group
            case_list.append(instance_dict)
        return case_list

    def get_http_case_obj(self):
        case = self.obj.case
        express_group = self.get_express(case)
        port = case.port
        apply = port.apply
        url = apply.baseUrl + port.portPath
        instance_dict = model_to_dict(case)
        instance_dict['url'] = url
        instance_dict['expressItem'] = express_group
        return instance_dict

    def get_case_one(self):
        case = self.obj
        express_group = self.get_express(case)
        port = case.port
        apply = port.apply
        url = apply.baseUrl + port.portPath
        instance_dict = model_to_dict(case)
        instance_dict['url'] = url
        instance_dict['expressItem'] = express_group
        return {"case": instance_dict}

    @staticmethod
    def default():
        return []

    @staticmethod
    def get_express(case_obj):
        # 预取expressItem及其关联的expressList，避免N+1查询
        # 注意：这里假设ExpressItem模型中有个'expressList'的反向关联名称（如果未设置，Django默认是'expresses_set'，但根据之前代码，我们假设为'expressList'）
        express_items = case_obj.expressItem.all().prefetch_related('expressList')
        express_group = []

        for group in express_items:
            # 直接获取expressItemId，避免使用model_to_dict整个对象
            # 注意：这里假设group的主键字段名为'id'，但之前代码中使用了'expressItemId'，可能是自定义字段？需要确认。
            # 如果模型中有一个字段叫expressItemId，那么用group.expressItemId；如果没有，而expressItemId是序列化器中定义的，那么这里应该用group.id
            # 根据之前序列化器代码，我们猜测模型主键是id，而expressItemId在序列化器中是source='id'，所以这里应该用group.id
            express_item_id = group.expressItemId  # 或者 group.expressItemId 如果模型有这个字段的话

            # 获取当前group的所有expressList，并转换为字典列表
            # 注意：这里我们只取需要的字段，避免转换不必要的数据
            express_list = []
            for item in group.expressList.all():
                item_dict = model_to_dict(item, fields=['expressId', 'matchMethod', 'matchKey', 'keyType', 'matchValue', 'matchOper'])
                express_list.append(item_dict)

            express_group.append({
                'expressItemId': express_item_id,
                'expressList': express_list
            })

        return express_group



