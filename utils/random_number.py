import random


class RandomNumber:

    def get_random_number(self, field_name: str, length: int, prefix: str = None) -> str:
        """
        获取随机数作为表内主键id
        :param field_name: 表字段名
        :param length: 长度
        :param prefix: 前缀
        :return: 随机数字字符串
        """
        while True:
            if prefix:
                number = prefix + ''.join([str(random.randint(0, 9)) for _ in range(length)])
                if not self.__class__.objects.filter(**{field_name: number}).exists():
                    return number
            else:
                number = ''.join([str(random.randint(0, 9)) for _ in range(length)])
                if not self.__class__.objects.filter(**{field_name: number}).exists():
                    return number
