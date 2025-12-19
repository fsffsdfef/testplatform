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
        "like": re.match,
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

    def get_assert(self, res_data: dict, express_group: list) -> dict:
        """获取断言结果"""
        group_assert_list = []
        final_list = []

        for index, express_obj in enumerate(express_group, 1):
            # 处理单个组的断言
            group_result = self._process_express_group(res_data, express_obj)
            group_assert_list.append(group_result)
            final_list.append(group_result["final"])

        return {
            'assertInfo': group_assert_list,
            'finalAssert': any(final_list)
        }

    def _process_express_group(self, res_data: dict, express_obj: dict) -> dict:
        """
        处理单个表达组
        :param res_data: 校验数据data
        :param express_obj: 规则组data
        :return:
        """
        item_final_list = list()
        item_assert_info_list = list()
        for express in express_obj["expressList"]:
            assert_result = self._process_single_express(res_data, express)
            item_final_list.append(assert_result['assert'])
            item_assert_info_list.append(assert_result)
        group_final = all(item_final_list)

        return {
        "groupID": express_obj.get("expressItemId"),
        "expressInfo": item_assert_info_list,
        "final": group_final
        }

    def _process_single_express(self, res_data: dict, express: dict) -> dict:
        """处理单个表达式"""
        # 提取表达式参数
        kwargs = dict()
        express_id = express.pop('expressId')
        match_key = express.pop('matchKey')
        match_opera = express.pop('matchOper')
        # 获取操作符
        opera = self._get_operator(match_opera)
        # 获取结果值
        result_value = self._get_nested_value(res_data, match_key.split("."))
        if match_opera != "!=null":
            key_type = express.pop('keyType')
            match_value = express.pop('matchValue')
            match_method = express.pop("matchMethod")
            # 构建断言信息
            assert_info = {
                'expressId': express_id,
                'oper': f'{match_method}[{match_key}] {match_opera} {match_value}',
                'assert': self._evaluate_assert(result_value=result_value,
                                                opera=opera,
                                                match_method=match_method,
                                                key_type=key_type,
                                                match_value=match_value)
            }
        else:
            # 构建断言信息
            assert_info = {
                'expressId': express_id,
                'oper': f'{match_key} {match_opera}',
                'assert': self._evaluate_assert(result_value, opera)
            }
        return assert_info

    def _get_nested_value(self, data: dict, keys: list) -> any:
        """获取要校验的值"""
        if not keys:
            return data
        current_key = keys[0]
        match = re.match(r'(\w+)\[(\d+)\]', current_key)
        if match:
            var_name = match.group(1)  # 'extPacks'
            index_num = match.group(2)  # '0' (字符串形式)
            if var_name not in data or data[var_name] is None:
                return None
            if index_num:
                current_value = data[var_name][int(index_num)]
        else:
            current_value = data[current_key]

        # 如果还有更多键且当前值是字典，继续递归
        if len(keys) > 1 and isinstance(current_value, dict):
            return self._get_nested_value(current_value, keys[1:])

        # 如果只有一个键，返回当前值
        if len(keys) == 1:
            return current_value

        # 如果还有更多键但当前值不是字典，返回None
        return None

    def _evaluate_assert(self,
                         result_value: any,
                         opera: callable,
                         key_type: str = None,
                         match_value: str = None,
                         match_method: str = None
                         ) -> bool:
        """评估断言结果"""
        try:
            if match_method and key_type and match_value:
                return opera(self._TYPE_DICT[match_method](result_value), self._TYPE_DICT[key_type](match_value))
            elif key_type and match_value:
                return opera(result_value, self._TYPE_DICT[key_type](match_value))
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
