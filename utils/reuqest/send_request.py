import requests
import operator
import json
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class RequestUtil(object):
    operator_dict = {
        '==': operator.eq,
        '<=': operator.le,
        '>=': operator.ge,
        '!=': operator.ne,
        '>': operator.lt,
        '<': operator.gt
    }

    type_dict = {
        'int': int,
        'str': str,
        'float': float
    }

    def __init__(self, url, method):
        self.method_type = 'http://'
        self.url = url
        self.method = method
        self.sess = requests.session()

    def get_adapter(self, total):
        retries = Retry(total=total, backoff_factor=1, status_forcelist=[500, 502, 503, 504],
                        allowed_methods=frozenset(["GET", "POST"]))
        adapter = HTTPAdapter(max_retries=retries)
        return adapter

    # def batch_send(self, case_list):
    #     res_list = []
    #     for apply_info in case_list:
    #         domains = apply_info.pop('domains', None)
    #         port_list = apply_info.pop('port', None)
    #         for port_info in port_list:
    #             method = port_info.pop('portMethod', None)
    #             port_name = port_info.pop('portName', None)
    #             cases = port_info.pop('httpCase', None)
    #             results = map(self.send, cases)
    #             res_list.append(list(results))
    #         return res_list

    def send(self, case_info):
        express_item_date = case_info.pop('expressItem', None)
        time_out = case_info.pop('timeOut', 3)
        retries = case_info.pop('retries', 0)
        header = case_info.pop('headers', None)
        body = case_info.pop('body', None)
        case_name = case_info.pop('caseName', None)
        if retries == 0:
            self.sess.mount(self.method_type, self.get_adapter(total=3))
        else:
            self.sess.mount(self.method_type, self.get_adapter(total=retries))
        try:
            res = self.sess.request(url=self.url, method=self.method, json=body, timeout=time_out)
            success = self.get_assert(res=res.json(), express_item_date=express_item_date)
        except requests.exceptions.RequestException:
            return {'msg': f'{case_name}执行失败', 'result': 'skip'}
        else:
            return {'caseName': case_name, 'header': header, 'req': body, 'res': res.json(), 'success': success}

    def get_operator(self, op_str):
        """将字符串类型的运算符转换为代码可以使用的运算符"""
        if op_str in self.operator_dict.keys():
            return self.operator_dict[op_str]
        else:
            raise ValueError(f"Invalid operator: {op_str}")

    def get_assert(self, res, express_item_date):
        """
        """
        for expressItem in express_item_date:
            express_list = expressItem.pop('expressList', None)
            for rule_info in express_list:
                match_key = rule_info.get('matchKey', None)
                key_type = rule_info.get('keyType', None)
                match_oper = rule_info.get('matchOper', None)
                match_value = rule_info.get('matchValue', None)
                res_date = res.get(match_key, None)
                if key_type in self.type_dict:
                    op_func = self.get_operator(match_oper)
                    result = op_func(res_date, self.type_dict[key_type](match_value))
                    return result
