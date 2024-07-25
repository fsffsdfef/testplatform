import json
import yaml


class ReadFile:

    CONFIG_PATH = "D:\\Users\\sw.fan\\Pycharm\\testplatform\\configs\\"

    def __init__(self, file_type: str, file_name: str):
        self.file_type = file_type
        self.file_name = file_name

    def distinguish(self):
        """
        根据文件类型，调用对应方法读取文件内容
        :return: 文件内容
        """
        if self.file_type == 'json':
            return self.read_json(self.file_name)
        if self.file_type == 'yaml':
            return self.read_ymal(self.file_name)

    def read_json(self, file_name: str) -> str:
        """
        读取json文件
        :param file_name: 文件名
        :return: json字符串
        """
        with open(file=self.CONFIG_PATH+file_name, mode='r', encoding='utf-8') as f:
            value = json.load(f)
            return value

    def read_ymal(self, file_name: str) -> list:
        """
        读取yaml文件
        :param file_name: 文件名
        :return: 返回list
        """
        with open(file=self.CONFIG_PATH+file_name, mode='r', encoding='utf-8') as f:
            value = yaml.load(stream=f, Loader=yaml.FullLoader)
            return value
