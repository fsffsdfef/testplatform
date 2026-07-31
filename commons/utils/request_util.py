import re
import logging
import requests
import json


log = logging.getLogger(__name__)


_CMD_MAP = {
        "jsonLoads": json.loads,
        "jsonDumps": json.dumps
    }


def get_kv(data, keys: str):
    """
    获取特殊指令key的数据
    :param data: 原始数据
    :param keys: 特殊指令
    :return: 获取特殊指令key的value
    """
    try:
        keys = keys.replace("$", "")

        match_data = None
        if "@" in keys:
            k_list = keys.split("@")
            data_key = k_list[0]
            if isinstance(data, dict):
                match_data = get_nested_value(data, data_key.split("."))
            elif isinstance(data, str):
                match_data = get_nested_value(json.loads(data), data_key.split("."))
            elif isinstance(data, requests.Response):
                match_data = get_nested_value(data.json(), data_key.split("."))
            if k_list[1] in _CMD_MAP:
                final_match_data = get_nested_value(_CMD_MAP[k_list[1]](match_data), k_list[2].split("."))
                return final_match_data
        else:
            if isinstance(data, dict):
                match_data = get_nested_value(data, keys.split("."))
            elif isinstance(data, requests.Response):
                match_data = get_nested_value(data.json(), keys.split("."))
            elif isinstance(data, str):
                match_data = get_nested_value(json.loads(data), keys.split("."))
            return match_data
    except Exception as e:
        log.error(f"异常报错，原因：{str(e)}")
        return None


def get_nested_value(data: dict, keys: list) -> any:
    """
    获取要校验的值
    :param data: 原始数据
    :param keys: 索引key
    :return: key所在的value
    """
    if not keys:
        return data

    try:
        current_key = keys[0]
        current_value = None
        match = re.match(r'(\w+)\[(\d+)]', current_key)
        if match:
            var_name = match.group(1)
            index_num = match.group(2)
            if var_name not in data or data[var_name] is None:
                return None
            if index_num:
                current_value = data[var_name][int(index_num)]
        else:
            current_value = data[current_key]

        # 如果还有更多键且当前值是字典，继续递归
        if len(keys) > 1 and isinstance(current_value, dict):
            return get_nested_value(current_value, keys[1:])
        # 如果只有一个键，返回当前值
        if len(keys) == 1:
            return current_value
    except KeyError as e:
        log.error(msg=f'{str(e)}不存在返回体中')
    # 如果还有更多键但当前值不是字典，返回None
        return None
