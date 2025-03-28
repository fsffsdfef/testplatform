from django.db import models
import random


class BaseModel(models.Model):
    """
    model模型抽象类
    """
    createdDate = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    updatedDate = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    createUser = models.CharField(verbose_name='创建人', max_length=20, null=True)
    updateUser = models.CharField(verbose_name='修改人', max_length=20, null=True)

    class Meta:
        abstract = True
        ordering = ["created_date"]

    def get_random_number(self, field_name: str, length: int = None, prefix: str = None, *args) -> any:
        """
        获取随机长度随机数字与前缀字符串拼接成新字符串左右查询条件，查询是否存在表内，不存在时返回
        @param field_name: 需要查询的字段名
        @param length: 随机数字长度
        @param prefix: 前缀
        @return: 前缀+随机数的字符串
        """
        while True:
            if prefix:
                number = prefix + ''.join([str(random.randint(0, 9)) for _ in range(length)])
                if not self.__class__.objects.filter(**{field_name: number}).exists():
                    return number
            else:
                number = random.randint(*args)
                if not self.__class__.objects.filter(**{field_name: number}).exists():
                    return number


