from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from django.core.cache import cache
from commons.utils.assert_util import assert_util
from commons.utils.request_util import get_nested_value, get_kv
from commons.utils.replace_util import replace_placeholders
import json
import uuid
import time
import requests
import operator
import logging
import asyncio
logger = logging.getLogger(__name__)


class RequestStrategy(ABC):
    """请求抽象基类"""

    @abstractmethod
    def send_action(self, data: List | Dict) -> List | Dict:
        """请求分发"""
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

    _CMD_MAP = {
        "jsonLoads": json.loads,
        "jsonDumps": json.dumps
    }

    # 全局变量

    def __init__(self, global_map: Dict = None):
        """初始化默认超时时间与请求头"""
        if global_map:
            self. _GLOBAL_MAP = global_map
        else:
            self._GLOBAL_MAP = {"SID": "FTEST"+str(uuid.uuid4())}
        self.default_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'RequestClient/1.0'
        }
        self.retries = 3
        self.sess = requests.session()

    def send_action(self, data: List | Dict) -> List | Dict:
        """
        请求分发
        :param data:
        :return:
        """
        try:
            if isinstance(data, List) and len(data) >= 1:
                sorted_data = sorted(data, key=operator.itemgetter("execution_order"))
                # sorted_data = list(map(self._set_session, data))
                res = self.batch_request(sorted_data)
                return res
            elif isinstance(data, Dict):
                res = self.send_request(data)
                return res
            else:
                return {"error": f"暂不支持{type(data)}类型数据"}
        except Exception as e:
            raise ValueError(f"{str(e)}")

    def batch_request(self, data_list: List) -> Dict:
        """
        批量执行
        :param data_list:
        :return:
        """
        answer_map = dict()
        # 数据预加载，获取前置，后置用例与排序常规用例
        is_first_case = [obj for obj in data_list if bool(obj.get("is_first"))]
        is_last_case = [obj for obj in data_list if bool(obj.get("is_last"))]
        remove_ids = {id(o) for o in is_last_case+is_first_case}
        data_list[:] = [o for o in data_list if id(o) not in remove_ids]
        # 执行用例获取答案
        answer_list = list(map(self.send_request, data_list))
        assert_list = list(map(lambda x: x['assert']['finalAssert'], answer_list))
        pass_percentage = self._get_pass_percentage(assert_list)
        answer_map['pass'] = pass_percentage
        answer_map['info'] = answer_list
        answer_map['global'] = self._GLOBAL_MAP
        return answer_map

    def send_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送请求
        :param data:
        :return: 请求与断言结果
        """
        try:
            case_info = data["case"]
            stream_key = data.get("streamKey", None)
            var_type = case_info.get("varType", False)
            case_id = case_info.pop('caseId', None)
            case_name = case_info.pop('caseName', None)
            retries = case_info.pop('retries', self.retries)
            headers = case_info.get("headers", None)
            global_map = data.pop('globalMap', None)
            if headers:
                if isinstance(headers, str):
                    headers = json.loads(headers)
                    case_info['headers'] = {**self.default_headers, **headers}
                else:
                    case_info['headers'] = {**self.default_headers, **headers}
            else:
                case_info['headers'] = self.default_headers
            body = case_info.pop("body")
            if body:
                body_net = replace_placeholders(body, self._GLOBAL_MAP, var_type=var_type)
                body_net = self._set_session(body_net)
                case_info["data"] = body_net
            case = {"method": "POST"}
            key_map = ["url", "headers", "data", "timeout", "expressItem"]
            for k in key_map:
                case[k] = case_info.pop(k, None)
            express_group = case.pop('expressItem', None)
            adapter = self.get_adapter(retries)
            self.sess.mount('http://', adapter)
            self.sess.mount('https://', adapter)
            if stream_key:
                res = self._send_stream_req(stream_key, case)
                final = assert_util.get_assert(req=body, res_data=res, express_group=express_group)
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
                final = assert_util.get_assert(req=body, res_data=res.json(), express_group=express_group)
                if global_map:
                    self._set_global_key(global_map=global_map, res=res)
            except requests.exceptions.RequestException as e:
                return {"caseId": case_id, "caseName": case_name,  "req": case,
                        "res": {"msg": f"{case_id}执行失败, {e}"}, "assert": {"finalAssert": False}, "msg": f"{case_id}执行失败, {e}", "success": "skip"}
            else:
                # logger.info(str(json.loads(res.json()["aitoken"])["messageId"]))
                data = {"caseId": case_id,
                        "caseName": case_name,
                        "req": case,
                        "res": res.json(),
                        "assert": final,
                        "global": self._GLOBAL_MAP,
                        # "trace": str(json.loads(res.json()["aitoken"])["messageId"])
                        }
                return data
        except Exception as e:
            logger.error(f"{str(e)}")
            import traceback
            traceback.print_exc()
            return {"msg": str(e)}

    def get_request_type(self) -> str:
        """请求类型"""
        return "HTTP"

    def get_adapter(self, total: int) -> HTTPAdapter:
        """
        自定义适配器
        @param total: 重试次数
        @return: 重试适配器实例
        """
        retries = Retry(total=total, backoff_factor=1,
                        status_forcelist=self._STATUS_FORCE,
                        allowed_methods=frozenset(['GET', 'POST']))
        adapter = HTTPAdapter(
            max_retries=retries,
            pool_maxsize=10,          # 单个主机的最大连接数
            pool_block=False
        )
        return adapter

    def _set_global_key(self, global_map: Dict, res: requests.Response):
        """设置全局变量"""
        for k, v in global_map.items():
            final_global_value = get_kv(data=res, keys=v)
            if final_global_value:
                self._GLOBAL_MAP[k] = final_global_value
                cache.set("global_map", self._GLOBAL_MAP)
            else:
                self._GLOBAL_MAP[k] = "获取失败"

    def _send_stream_req(self, stream_key, case, num=0) -> Dict:
        """流式请求执行逻辑"""
        # 防止测试环境缓存写入过慢，导致执行失败
        time.sleep(1)
        num = num
        data = case['data']
        if isinstance(data, str):
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
            if res['readyForData'] is False or res['streamOver'] is None:
                num += 1
                self._send_stream_req(stream_key, case, num)

        return {"msg": "超过最大片数"}

    @staticmethod
    def _get_pass_percentage(assert_list):
        """获取通过率"""
        if len(assert_list) == 0:
            return 0
        return round(sum(assert_list) / len(assert_list) * 100, 2)

    def _set_session(self, data):
        """初始化sid"""
        try:
            sid = self._GLOBAL_MAP["SID"]
            body_obj = json.loads(data)
            if "sessionId" in body_obj.keys():
                body_obj["sessionId"] = sid
            body_str = json.dumps(body_obj)
            return body_str
        except Exception as e:
            logger.error(f"{str(e)}")
            return data


class DubboRequest(RequestStrategy):
    pass


class UIRequest(RequestStrategy):

    def __init__(self):
        pass

    def click(self, selector: str):
        pass