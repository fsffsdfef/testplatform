import re


def get_nested_value(data: dict, keys: list) -> any:

    """获取要校验的值"""
    if not keys:
        return data
    current_key = keys[0]
    current_value = None
    match = re.match(r'(\w+)\[(\d+)]', current_key)
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
        return get_nested_value(current_value, keys[1:])
    # 如果只有一个键，返回当前值
    if len(keys) == 1:
        return current_value
    # 如果还有更多键但当前值不是字典，返回None
    return None
