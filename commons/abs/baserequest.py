from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from commons.utils.assert_util import assert_util
from commons.utils.request_util import get_nested_value
from commons.utils.replace_util import replace_placeholders
import json
import time
import requests
import operator


class RequestStrategy(ABC):
    """请求抽象基类"""

    @abstractmethod
    def send_action(self, data: List | Dict) -> List | Dict:
        pass

    @abstractmethod
    def batch_request(self, data: list) -> list:
        """批量请求"""
        pass

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

    def __init__(self, timeout: int = 30):
        """初始化默认超时时间与请求头"""
        self. _GLOBAL_MAP = {}
        self.timeout = timeout
        self.default_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'RequestClient/1.0'
        }
        self.sess = requests.session()

    def send_action(self, data: List | Dict) -> List | Dict:
        if isinstance(data, List) and len(data) >= 1:
            sorted_data = sorted(data, key=operator.itemgetter("execution_order"))
            res = self.batch_request(sorted_data)
            return res
        elif isinstance(data, Dict):
            res = self.send_request(data)
            return res
        else:
            return {"msg": "暂不支持"}

    def batch_request(self, data_list: List) -> List:
        # 根据序号排序，并抽出前置与后置用例
        is_first_case = [obj for obj in data_list if bool(obj.get("is_first"))]
        is_last_case = [obj for obj in data_list if bool(obj.get("is_last"))]
        remove_ids = {id(o) for o in is_last_case+is_first_case}
        data_list[:] = [o for o in data_list if id(o) not in remove_ids]
        # 执行用例获取答案
        answer_list = list(map(self.send_request, data_list))
        return answer_list

    def send_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            case_info = data["case"]
            stream_key = data.get("streamKey", None)
            case_id = case_info.pop('caseId', None)
            case_name = case_info.pop('caseName', None)
            retries = case_info.pop('retries', 0)
            headers = data.pop("headers", None)
            global_map = data.pop('globalList', None)
            if headers:
                case_info['headers'] = self.default_headers.update(headers)
            else:
                case_info['headers'] = self.default_headers
            body = case_info.pop("body")
            if body:
                body_net = replace_placeholders(body, self._GLOBAL_MAP)
                case_info["data"] = body_net
            case = {"method": "POST"}
            key_map = ["url", "headers", "data", "timeout", "expressItem"]
            for k in key_map:
                case[k] = case_info.pop(k, None)
            express_group = case.pop('expressItem', None)
            adapter = self.get_adapter(retries)
            self.sess.mount('http://', adapter)
            if stream_key:
                res = self._send_stream_req(stream_key, case)
                final = assert_util.get_assert(res_data=res, express_group=express_group)
                data = {"caseId": case_id,
                        "caseName": case_name,
                        "req": case,
                        "res": res,
                        "assert": final,
                        "global": global_map
                        }
                return data
            try:
                res = self.sess.request(**case)
                final = assert_util.get_assert(res_data=res.json(), express_group=express_group)
                if global_map:
                    self._set_global_key(global_map=global_map, res=res)
            except requests.exceptions.RequestException as e:
                return {"caseId": case_id, "caseName": case_name, 'msg': f'{case_id}执行失败, {e}', 'success': 'skip'}
            else:
                data = {"caseId": case_id,
                        "caseName": case_name,
                        "req": case,
                        "res": res.json(),
                        "assert": final,
                        "global": global_map
                        }
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

    def _set_global_key(self, global_map: Dict, res: requests.Response):
        """设置全局变量"""
        for k, v in global_map.items():
            v = get_nested_value(res.json(), v.split("."))
            self._GLOBAL_MAP[k] = v

    def _send_stream_req(self, stream_key, case) -> Dict:
        num = 0
        data = json.loads(case['data'])
        data[stream_key] = num
        case['data'] = json.dumps(data)
        while num < 10:
            try:
                res = self.sess.request(**case).json()
            except Exception as e:
                return {"msg": f"请求失败，原因：{str(e)}"}
            if res['streamOver'] is True and res['fullData']:
                return res
            if res['readyForData'] is False:
                continue
            if res['streamOver'] is None:
                num += 1
                continue
        return {"msh": "超过最大片数"}



