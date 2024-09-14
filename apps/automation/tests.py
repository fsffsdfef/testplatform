from django.test import TestCase
import os
import django
from django.core.cache import cache
# 设置 DJANGO_SETTINGS_MODULE 环境变量（引入settings文件）
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testplatform.settings')
# 加载 Django 项目配置
django.setup()
# Create your tests here.
from apps.automation.models.interface import Apply
from apps.common.sers.departser import ApplySer
import json


class UnitTestCase(TestCase):

    def test_a(self):
        value = Apply.objects.filter(appId='100009299')
        ser = ApplySer(instance=value, many=True)
        case_info = json.dumps(ser.data, ensure_ascii=False)
        # for i in json.loads(case_info):
        #     print(f'这是用例：{i.get("httpCase")}')
        # for i in case_info:
        #     print(json.loads(i))
        for i in ser.data:
            print(i.get('port'))

v = UnitTestCase()
v.test_a()
