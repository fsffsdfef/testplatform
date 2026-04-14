import re
import json


def replace_placeholders(text, data_dict, var_type):
    """
    识别字符串中的 {placeholder}，并用 data_dict[placeholder] 的值替换
    保持原始值的格式（如果是字符串，保持字符串格式）

    参数:
        text: 包含占位符的字符串
        data_dict: 包含键值对的字典

    返回:
        替换后的字符串
    """
    # 正则表达式匹配 {xxx} 格式的占位符
    pattern = r'\${(\w+)\}'

    # 使用回调函数进行替换
    def replacement(match):
        key = match.group(1)  # 提取占位符内的key
        if key in data_dict:
            value = data_dict[key]
            # 如果值是字符串，需要转义并保持字符串格式
            if var_type:
                json_str = json.dumps(value, ensure_ascii=False)
                return json_str
            else:
                return value

        else:
            # 如果字典中没有该key，返回空字符串
            return '"全局无此变量"'

    return re.sub(pattern, replacement, text)
