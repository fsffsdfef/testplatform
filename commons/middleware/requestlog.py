# 在 your_app/middleware.py 或 common/middleware.py
import threading
import json
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone

# 线程局部存储
_request_local = threading.local()


class RequestLogMiddleware(MiddlewareMixin):
    """存储请求上下文到线程局部存储"""

    def process_request(self, request):
        """
        请求开始时执行
        """
        # 清空前一个线程的数据（安全起见）
        if hasattr(_request_local, 'request_data'):
            delattr(_request_local, 'request_data')

        # 准备请求数据（注意：此时还不知道响应状态码）
        request_data = {
            'path': request.path,
            'method': request.method,
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'client_ip': self._get_client_ip(request),
            'user_id': request.user.id if request.user.is_authenticated else None,
            'username': request.user.username if request.user.is_authenticated else 'anonymous',
            'query_params': self._safe_serialize(request.GET.dict()),
            'form_data': self._safe_serialize(request.POST.dict()),
            'headers': self._get_safe_headers(request),
            'request_start_time': timezone.now(),
            'request_body': self._get_request_body(request),
        }

        # 存储到线程局部存储
        _request_local.request_data = request_data

        # 设置请求开始时间（用于计算响应时间）
        request._logging_start_time = timezone.now()

        return None

    @staticmethod
    def process_response(request, response):
        """
        响应完成时执行
        """
        if hasattr(_request_local, 'request_data'):
            request_data = _request_local.request_data

            # 计算响应时间
            if hasattr(request, '_logging_start_time'):
                duration = (timezone.now() - request._logging_start_time).total_seconds()
                request_data['duration'] = duration

            # 添加响应信息
            request_data['status_code'] = response.status_code
            request_data['response_size'] = len(response.content) if hasattr(response, 'content') else 0
            request_data['response_content_type'] = response.get('Content-Type', '')

            # 更新存储的数据
            _request_local.request_data = request_data

            # 清理请求时间属性
            if hasattr(request, '_logging_start_time'):
                delattr(request, '_logging_start_time')

        return response

    @staticmethod
    def process_exception(request, exception):
        """
        处理异常
        """
        if hasattr(_request_local, 'request_data'):
            _request_local.request_data['exception'] = str(exception)
        return None

    @staticmethod
    def _get_client_ip(request):
        """获取客户端IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @staticmethod
    def _get_safe_headers(request):
        """获取安全的请求头信息"""
        safe_headers = {}
        sensitive_keys = ['authorization', 'cookie', 'password', 'token', 'secret']

        for key, value in request.META.items():
            if key.startswith('HTTP_'):
                header_name = key[5:].replace('_', '-').lower()
                # 过滤敏感头信息
                if not any(sensitive in header_name.lower() for sensitive in sensitive_keys):
                    safe_headers[header_name] = str(value)[:200]  # 截断过长的值

        return safe_headers

    @staticmethod
    def _get_request_body(request):
        """安全获取请求体"""
        try:
            # 对于 JSON 请求
            if request.content_type == 'application/json' and request.body:
                import json
                return json.loads(request.body.decode('utf-8')[:1000])  # 限制大小
            # 对于表单数据，已经在 form_data 中处理
            return None
        except Exception:
            return None

    @staticmethod
    def _safe_serialize(data):
        """安全序列化数据"""
        try:
            # 尝试序列化为 JSON
            return json.dumps(data, ensure_ascii=False)
        except (TypeError, ValueError):
            # 失败则转为字符串
            return str(data)


def get_request_data():
    """
    获取当前线程的请求数据
    在日志处理器中调用
    """
    return getattr(_request_local, 'request_data', None)