# apps/automatic/tests.py
"""
针对 testplatformservice/testplatform 项目的优化测试脚本
"""
import os
import sys

# 设置项目根路径
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(PROJECT_ROOT)

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

try:
    import django
    django.setup()
except Exception as e:
    print(f"初始化Django失败: {e}")
    sys.exit(1)

# 安全警告
from django.conf import settings
if 'prod' in settings.DATABASES['default']['NAME']:
    print("⚠️ 警告：您正在连接生产数据库！")
    confirm = input("确认继续？(yes/no): ")
    if confirm.lower() != 'yes':
        print("操作已取消")
        sys.exit(1)

# 导入应用模块
try:
    from apps.automatic.models import SuitModel
    from commons.utils.getcasedata import GetCaseData
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("当前Python路径:")
    for p in sys.path:
        print(f" - {p}")
    sys.exit(1)
# 标准导入（在Django设置后）
from commons.utils.getcasedata import GetCaseData
from commons.utils.request import AutomatedRequest
from apps.automatic.models import SuitModel
from apps.automatic.sers import SuitSer

a = SuitModel.objects.get(suitId=9828)
print(a)
# b = GetCaseData(a).get_case('http')
# AutomatedRequest(b[0]).http_send()
