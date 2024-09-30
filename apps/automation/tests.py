import time

from django.test import TestCase
import os
import django
from django.core.cache import cache
# 设置 DJANGO_SETTINGS_MODULE 环境变量（引入settings文件）
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testplatform.settings')
# 加载 Django 项目配置
django.setup()
# Create your tests here.
from apps.common.modelss.depart_and_app import Apply
from apps.common.sers.depart_app_menu_ser import ApplySer
import json
from celerys.tasks import *
from celerys import celery_app
import subprocess
import psutil


class UnitTestCase(TestCase):

    def test_a(self):
        value = Apply.objects.filter(appId='100068188')
        ser = ApplySer(instance=value, many=True)
        case_info = json.dumps(ser.data, ensure_ascii=False)
        # for i in json.loads(case_info):
        #     print(f'这是用例：{i.get("httpCase")}')
        # for i in case_info:
        #     print(json.loads(i))
        # for i in ser.data:
        #     print(i.get('port'))
        port_list = list(
            map(lambda cases: cases.pop('port', None) if cases.pop('port', None) is not None else {"code": 100},
                json.loads(case_info)))
        print(port_list)
        print(json.loads(case_info))

    def test_demo1(self):
        cmd = 'celery -A celerys worker --loglevel=info -P eventlet'
        subprocess.run(cmd)
        self.test_ansyc_demo()

    def test_ansyc_demo(self):
        result = task_demo.delay()
        res = celery_app.AsyncResult(result.id)
        print(res)
        result1 = task_demo1.delay()
        res1 = celery_app.AsyncResult(result1.id)
        print(res1)
        result2 = task_demo2.delay()
        res2 = celery_app.AsyncResult(result2.id)
        print(res2)

    def test_12(self):
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # 获取进程的名称和进程 ID
                name = proc.info['name']
                pid = proc.info['pid']

                # 如果进程名称中包含 "celery"，则输出进程的名称和进程 ID
                if 'celery' in name:
                    print(f"Found celery process: {name} (pid={pid})")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass


v = UnitTestCase()
v.test_a()
