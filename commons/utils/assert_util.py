from commons.utils.request_util import get_nested_value, get_kv
import operator
import re


class AssertUtil:
    # 规则映射对象
    _OPERATOR_DICT = {
        '==': operator.eq,
        '<=': operator.le,
        '>=': operator.ge,
        '!=': operator.ne,
        '>': operator.lt,
        '<': operator.gt,
        'in': operator.contains,
        "!=null": operator.is_not,
        "like": re.search,
        "re": re.search
    }
    # 被校验的答案类型枚举
    _TYPE_DICT = {
        'int': int,
        'str': str,
        'float': float,
        'len': len,
        'list': list
    }
    _METHOD_MAP = {
        'len': len,
        'max': max,
        'sum': sum
    }

    def get_assert(self, req: dict, res_data: dict, express_group: list) -> dict:
        """获取断言结果"""
        group_assert_list = []
        final_list = []

        for index, express_obj in enumerate(express_group, 1):
            # 处理单个组的断言
            group_result = self._process_express_group(req, res_data, express_obj)
            group_assert_list.append(group_result)
            final_list.append(group_result["final"])

        return {
            'assertInfo': group_assert_list,
            'finalAssert': any(final_list)
        }

    def _process_express_group(self, req: dict, res_data: dict, express_obj: dict) -> dict:
        """
        处理单个表达组
        :param res_data: 校验数据data
        :param express_obj: 规则组data
        :return:
        """
        item_final_list = list()
        item_assert_info_list = list()
        for express in express_obj["expressList"]:
            assert_result = self._process_single_express(req, res_data, express)
            item_final_list.append(assert_result['assert'])
            item_assert_info_list.append(assert_result)
        group_final = all(item_final_list)

        return {
        "groupID": express_obj.get("expressItemId"),
        "expressInfo": item_assert_info_list,
        "final": group_final
        }

    def _process_single_express(self, req: dict, res_data: dict, express: dict) -> dict:
        """处理单个表达式"""
        # 提取表达式参数
        express_id = express.pop('expressId')
        match_key = express.pop('matchKey')
        match_opera = express.pop('matchOper')
        # 获取操作符
        opera = self._get_operator(match_opera)
        # 获取结果值
        result_value = get_nested_value(res_data, match_key.split("."))
        if match_opera != "!=null":
            key_type = express.pop('keyType')
            match_value = express.pop('matchValue')
            if "$" in match_value:
                match_value = get_kv(req, match_value)
            match_method = express.pop("matchMethod")
            # 构建断言信息
            assert_info = {
                'expressId': express_id,
                'oper': f'{match_method}[{match_key}] {match_opera} {match_value}',
                'assert': self._evaluate_assert(result_value=result_value,
                                                opera=opera,
                                                match_method=match_method,
                                                key_type=key_type,
                                                match_value=match_value,
                                                match_opera=match_opera
                                                )
            }
        else:
            # 构建断言信息
            assert_info = {
                'expressId': express_id,
                'oper': f'{match_key} {match_opera}',
                'assert': self._evaluate_assert(result_value, opera)
            }
        return assert_info

    def _evaluate_assert(self,
                         result_value: any,
                         opera: callable,
                         match_opera: str = None,
                         key_type: str = None,
                         match_value: str = None,
                         match_method: str = None
                         ) -> bool:
        """评估断言结果"""
        if "$" in match_value:
            pass
        try:
            if opera.__name__ == "search":
                if match_opera == "like":
                    return bool(opera(re.escape(self._TYPE_DICT[key_type](match_value)), result_value))
                if match_opera == "re":
                    return bool(opera(self._TYPE_DICT[key_type](match_value), result_value))
            if match_method and match_method != "0" and key_type and match_value:
                return opera(self._TYPE_DICT[match_method](result_value), self._TYPE_DICT[key_type](match_value))
            elif key_type and match_value:
                return bool(opera(result_value, self._TYPE_DICT[key_type](match_value)))
            else:
                return opera(result_value, None)
        except (ValueError, TypeError) as e:
            print(f"断言评估失败: {e}")
            return False

    def _get_operator(self, opera: str):
        """
        获取要使用的运算实例
        :param opera:
        :return:
        """
        if opera in self._OPERATOR_DICT.keys():
            return self._OPERATOR_DICT[opera]
        else:
            raise ValueError(f"Invalid operator: {opera}")


assert_util = AssertUtil()
