import requests
import operator
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class AutomatedRequest(object):
    REQUEST_TYPE = {
        "http": 1,
        "dubbo": 2,
        "webUi": 3,
        "appUi": 4
    }

    # 规则映射对象
    OPERATOR_DICT = {
        '==': operator.eq,
        '<=': operator.le,
        '>=': operator.ge,
        '!=': operator.ne,
        '>': operator.lt,
        '<': operator.gt,
        'in': operator.contains
    }

    # 被校验的答案类型枚举
    TYPE_DICT = {
        'int': int,
        'str': str,
        'float': float,
        'len': len
    }

    METHOD_MAP = {
        'len': len,
        'max': max,
        'sum': sum
    }

    # 触发重试的状态码
    STATUS_FORCE = [500, 502, 503, 504]

    def __init__(self, case_data):
        self.case_data = case_data
        self.sess = requests.session()

    def action(self, request_type):

        if request_type not in self.REQUEST_TYPE:
            return {"msg": "暂不支持此类型操作"}
        return []

    def http_send(self):
        case_id = self.case_data.pop('caseId', None)
        retries = self.case_data.pop('retries', 0)
        self.case_data["data"] = self.case_data.pop("body")
        case = {"method": "POST"}
        key_map = ["url", "headers", "data", "timeout", "expressItem"]
        for k in key_map:
            case[k] = self.case_data.pop(k, None)
        express_group = case.pop('expressItem')
        adapter = self.get_adapter(retries)
        self.sess.mount('http://', adapter)
        try:
            res = self.sess.request(**case)
            final = self.get_assert(res_data=res.json(), express_group=express_group)
        except requests.exceptions.RequestException as e:
            return {'code': 1000001, 'msg': f'{case_id}执行失败, {e}', 'success': 'skip'}
        else:
            data = {"req": case, "res": res.json(), "success": final}
            return data

    def get_adapter(self, total):
        """
        请求重试配置
        @param total: 重试次数
        @return: 重试适配器实例
        """
        retries = Retry(total=total, backoff_factor=1,
                        status_forcelist=self.STATUS_FORCE, allowed_methods=frozenset(['GET', 'POST']))
        adapter = HTTPAdapter(max_retries=retries)
        return adapter

    def get_assert(self, res_data: dict, express_group: list) -> dict:
        result_map = list()
        assert_map = list()
        result_answer = dict()
        for express_obj in express_group:
            for express in express_obj['expressList']:
                assert_info = dict()
                match_key = express.pop('matchKey')
                key_type = express.pop('keyType')
                match_value = express.pop('matchValue')
                match_opera = express.pop('matchOper')
                opera = self.get_operator(match_opera)
                result_value = eval(f'{res_data}{match_key}')
                result = opera(result_value, self.TYPE_DICT[key_type](match_value))
                assert_info['msg'] = f'{match_key} {match_opera} {match_value}'
                assert_info['assert'] = result
                result_map.append(result)
                assert_map.append(assert_info)
        final = all(result_map)
        result_answer['assetInfo'] = assert_map
        result_answer['success'] = final
        return result_answer

    def get_operator(self, opera: str):

        if opera in self.OPERATOR_DICT.keys():
            return self.OPERATOR_DICT[opera]
        else:
            raise ValueError(f"Invalid operator: {opera}")
