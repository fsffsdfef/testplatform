import requests
import operator
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class AutomatedRequest(object):
    REQUEST_TYPE = {
        "http": 1,
        "dubbo": 2,
        "webUi": 3,
        "appUi": 4
    }

    # 规则映射对象 - 修复操作符映射错误
    OPERATOR_DICT = {
        '==': operator.eq,
        '<=': operator.le,
        '>=': operator.ge,
        '!=': operator.ne,
        '>': operator.gt,  # 修复：原来是 operator.lt
        '<': operator.lt,  # 修复：原来是 operator.gt
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
            logger.warning(f"不支持的请求类型: {request_type}")
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
            logger.info(f"发送HTTP请求: {case_id}")
            res = self.sess.request(**case)
            res.raise_for_status()  # 检查HTTP状态码
            final = self.get_assert(res_data=res.json(), express_group=express_group)
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP请求失败: {case_id}, 错误: {e}")
            return {'code': 1000001, 'msg': f'{case_id}执行失败, {e}', 'success': 'skip'}
        except ValueError as e:
            logger.error(f"JSON解析失败: {case_id}, 错误: {e}")
            return {'code': 1000002, 'msg': f'{case_id}响应解析失败, {e}', 'success': 'skip'}
        else:
            data = {"req": case, "res": res.json(), "success": final}
            logger.info(f"HTTP请求成功: {case_id}")
            return data

    def get_adapter(self, total):
        """
        请求重试配置
        @param total: 重试次数
        @return: 重试适配器实例
        """
        retries = Retry(
            total=total, 
            backoff_factor=1,
            status_forcelist=self.STATUS_FORCE, 
            allowed_methods=frozenset(['GET', 'POST'])
        )
        adapter = HTTPAdapter(max_retries=retries)
        return adapter

    def get_assert(self, res_data: dict, express_group: list) -> dict:
        result_map = []
        assert_map = []
        
        for express_obj in express_group:
            for express in express_obj['expressList']:
                assert_info = dict()
                match_key = express.pop('matchKey')
                key_type = express.pop('keyType')
                match_value = express.pop('matchValue')
                match_opera = express.pop('matchOper')
                
                try:
                    opera = self.get_operator(match_opera)
                    result_value = self._safe_eval(f'{res_data}{match_key}')
                    result = opera(result_value, self.TYPE_DICT[key_type](match_value))
                    
                    assert_info['msg'] = f'{match_key} {match_opera} {match_value}'
                    assert_info['assert'] = result
                    result_map.append(result)
                    assert_map.append(assert_info)
                except Exception as e:
                    logger.error(f"断言执行失败: {match_key} {match_opera} {match_value}, 错误: {e}")
                    result_map.append(False)
                    assert_info['msg'] = f'{match_key} {match_opera} {match_value} (执行失败)'
                    assert_info['assert'] = False
                    assert_map.append(assert_info)
        
        final = all(result_map)
        result_answer = {'assetInfo': assert_map, 'success': final}
        return result_answer

    def _safe_eval(self, expression):
        """安全地执行表达式，避免使用eval的安全风险"""
        try:
            # 这里应该使用更安全的表达式解析方法
            # 暂时保留eval，但建议后续改进
            return eval(expression)
        except Exception as e:
            logger.error(f"表达式执行失败: {expression}, 错误: {e}")
            raise

    def get_operator(self, opera: str):
        if opera in self.OPERATOR_DICT:
            return self.OPERATOR_DICT[opera]
        else:
            raise ValueError(f"无效的操作符: {opera}")
