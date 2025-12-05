import logging
from apps.log.models import LogEntry


class DatabaseHandler(logging.Handler):
    def emit(self, record):
        try:
            LogEntry.objects.create(
                logger_name=record.name,
                level=record.levelname,
                message=record.getMessage(),
                trace=record.exc_text if record.exc_info else None
            )
        except Exception as e:
            # 避免日志记录失败导致循环错误
            logging.getLogger('django.db.backends').error(
                f"Failed to save log to database: {e}"
            )
