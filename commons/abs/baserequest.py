from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from commons.utils.assert_util import assert_util
import json
import time
import requests


class RequestStrategy(ABC):
    """请求抽象基类"""

    @abstractmethod
    def send_request(self, data: dict) -> dict:
        """发送请求，获取返回数据"""
        pass

    @abstractmethod
    def get_request_type(self) -> str:
        """获取请求类型"""
        pass


class HttpRequestStrategy(RequestStrategy):
    # 触发重试的状态码
    _STATUS_FORCE = [500, 502, 503, 504]

    # 全局变量
    _GLOBAL = {}

    def __init__(self, timeout: int = 30, headers: Dict[str, str] = None):
        """初始化默认超时时间与请求头"""
        self.timeout = timeout
        self.default_headers = headers or {
            'Content-Type': 'application/json',
            'User-Agent': 'RequestClient/1.0'
        }
        self.sess = requests.session()

    def send_request(self, data: Dict[str, any]) -> Dict[str, any]:
        try:
            case_info = data["case"]
            case_id = case_info.pop('caseId', None)
            case_name = case_info.pop('caseName', None)
            retries = case_info.pop('retries', 0)
            global_map = case_info.get("globalList")
            # headers = data.get("headers", None)
            # if headers == "":
            #     headers = None
            # body = data.get("body", None)
            # if headers:
            #     data["headers"] = json.loads(headers)
            # if body:
            #     data["body"] = json.loads(body)
            case_info["data"] = case_info.pop("body")
            case = {"method": "POST"}
            key_map = ["url", "headers", "data", "timeout", "expressItem"]
            for k in key_map:
                case[k] = case_info.pop(k, None)
            express_group = case.pop('expressItem', None)
            adapter = self.get_adapter(retries)
            self.sess.mount('http://', adapter)
            try:
                res = self.sess.request(**case)
                final = assert_util.get_assert(res_data=res.json(), express_group=express_group)

            except requests.exceptions.RequestException as e:
                return {"caseId": case_id, "caseName": case_name, 'msg': f'{case_id}执行失败, {e}', 'success': 'skip'}
            else:
                data = {"caseId": case_id, "caseName": case_name, "req": case, "res": res.json(), "assert": final}
                return data
        except Exception as e:
            print(f"有报错哟{e}")
            import traceback
            traceback.print_exc()
            return {"msg": str(e)}

    def get_request_type(self) -> str:
        return "HTTP"

    def get_adapter(self, total: int) -> HTTPAdapter:
        """
        请求重试配置
        @param total: 重试次数
        @return: 重试适配器实例
        """
        retries = Retry(total=total, backoff_factor=1,
                        status_forcelist=self._STATUS_FORCE, allowed_methods=frozenset(['GET', 'POST']))
        adapter = HTTPAdapter(max_retries=retries)
        return adapter

    def set_global_key(self, request):
        """设置全局变量"""
        pass
