import logging
import traceback
import threading
from django.utils import timezone
from django.db import transaction


class DatabaseLogHandler(logging.Handler):
    """将日志写入数据库的处理器（延迟导入模型）"""

    def __init__(self, level=logging.NOTSET):
        super().__init__(level)
        self._buffer = []
        self._buffer_size = 2  # 批量写入大小
        self._lock = threading.Lock()
        self._model = None  # 延迟加载模型

    def _get_model(self):
        """延迟获取模型，避免在 Django 启动时导入"""
        if self._model is None:
            try:
                from apps.log.models import LogEntry
                self._model = LogEntry
            except Exception as e:
                # 如果模型还未加载，返回 None
                print(f"Warning: Cannot import LogEntry model: {e}")
                return None
        return self._model

    def emit(self, record):
        """处理日志记录"""
        try:
            # 检查 Django 是否已加载
            try:
                from django.apps import apps
                if not apps.ready:
                    # Django 未就绪，跳过数据库写入
                    return
            except Exception:
                # 如果无法检查，也跳过
                return

            # 获取模型
            LogEntry = self._get_model()
            if LogEntry is None:
                return

            request_data = None
            try:
                from commons.middleware.requestlog import get_request_data
                request_data = get_request_data()
            except ImportError as e:
                request_data = getattr(threading.current_thread(), "request_data", None)
            except Exception as e:
                # 其他错误
                print(f"获取请求数据失败: {e}")
                request_data = None
            # 获取异常信息
            exc_info = None
            if record.exc_info:
                exc_info = ''.join(traceback.format_exception(*record.exc_info))

            # 构建日志数据
            log_data = {
                'level': record.levelname,
                'logger_name': record.name,
                'message': record.getMessage(),
                'module': record.module if hasattr(record, 'module') else None,
                'func_name': record.funcName if hasattr(record, 'funcName') else None,
                'line_no': record.lineno if hasattr(record, 'lineno') else None,
                'thread': str(threading.current_thread().ident),
                'process': str(record.process) if hasattr(record, 'process') else None,
                'exception_info': exc_info,
                'created_at': timezone.now(),
            }

            if request_data:
                log_data['extra_data'] = {
                    'request_path': request_data.get('path'),
                    'request_method': request_data.get('method'),
                    'client_ip': request_data.get('client_ip'),
                    'user_id': request_data.get('user_id'),
                    'username': request_data.get('username'),
                    'status_code': request_data.get('status_code'),
                    'duration': request_data.get('duration'),
                    'user_agent': request_data.get('user_agent', '')[:500],  # 限制长度
                }

            # 提取额外数据
            import json
            extra_data = {}
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                               'filename', 'module', 'lineno', 'funcName', 'created',
                               'msecs', 'relativeCreated', 'thread', 'threadName',
                               'processName', 'process', 'message', 'exc_info', 'exc_text',
                               'stack_info']:
                    try:
                        # 尝试序列化
                        json.dumps(value)
                        extra_data[key] = value
                    except (TypeError, ValueError):
                        extra_data[key] = str(value)

            log_data['extra_data'] = extra_data

            # 添加到缓冲区
            with self._lock:
                self._buffer.append(log_data)

                # 批量写入
                if len(self._buffer) >= self._buffer_size:
                    self._flush_buffer()

        except Exception:
            # 避免日志处理器本身出错导致循环
            self.handleError(record)

    def _flush_buffer(self):
        """刷新缓冲区到数据库"""
        if not self._buffer:
            return

        LogEntry = self._get_model()
        if LogEntry is None:
            self._buffer.clear()
            return

        try:
            with transaction.atomic():
                logs_to_create = [
                    LogEntry(**log_data)
                    for log_data in self._buffer
                ]
                LogEntry.objects.bulk_create(logs_to_create, ignore_conflicts=True)
                self._buffer.clear()
        except Exception as e:
            # 如果数据库写入失败，至少记录到控制台
            print(f"Failed to write logs to database: {e}")
            self._buffer.clear()

    def flush(self):
        """强制刷新缓冲区"""
        with self._lock:
            self._flush_buffer()

    def close(self):
        """关闭处理器时刷新缓冲区"""
        self.flush()
        super().close()