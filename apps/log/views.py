from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
from .models import LogEntry
from commons.cusntom.response import CustomResponse
from .ser import LogEntrySer
from rest_framework.viewsets import ModelViewSet
from commons.cusntom.pagination import CustomPage
import json


class Log(ModelViewSet):
    queryset = LogEntry.objects.all()
    serializer_class = LogEntrySer
    permission_classes = []
    pagination_class = CustomPage

def log_list_view(request):
    """日志列表视图"""
    # 获取查询参数
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 50))
    level = request.GET.get('level', '')
    logger_name = request.GET.get('logger', '')
    keyword = request.GET.get('keyword', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    # 构建查询
    queryset = LogEntry.objects.all()

    if level:
        queryset = queryset.filter(level=level)

    if logger_name:
        queryset = queryset.filter(logger_name__icontains=logger_name)

    if keyword:
        queryset = queryset.filter(
            Q(message__icontains=keyword) |
            Q(module__icontains=keyword) |
            Q(func_name__icontains=keyword)
        )

    if start_date:
        queryset = queryset.filter(created_at__gte=start_date)

    if end_date:
        queryset = queryset.filter(created_at__lte=end_date)

    # 分页
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)

    # 格式化数据
    logs = []
    for log in page_obj:
        logs.append({
            'id': log.id,
            'level': log.level,
            'logger_name': log.logger_name,
            'message': log.message,
            'module': log.module,
            'func_name': log.func_name,
            'line_no': log.line_no,
            'thread': log.thread,
            'process': log.process,
            'exception_info': log.exception_info,
            'extra_data': log.extra_data,
            'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        })

    # 返回 JSON 或 HTML
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'code': 0,
            'message': 'success',
            'data': {
                'logs': logs,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total': paginator.count,
                    'total_pages': paginator.num_pages,
                }
            }
        })

    # HTML 渲染
    context = {
        'logs': page_obj,
        'levels': LogEntry.LEVEL_CHOICES,
        'current_level': level,
        'current_logger': logger_name,
        'keyword': keyword,
    }
    return render(request, 'logs/list.html', context)


def log_detail_view(request, log_id):
    """日志详情视图"""
    try:
        log = LogEntry.objects.get(id=log_id)
        data = {
            'id': log.id,
            'level': log.level,
            'logger_name': log.logger_name,
            'message': log.message,
            'module': log.module,
            'func_name': log.func_name,
            'line_no': log.line_no,
            'thread': log.thread,
            'process': log.process,
            'exception_info': log.exception_info,
            'extra_data': json.dumps(log.extra_data, indent=2, ensure_ascii=False) if log.extra_data else '',
            'created_at': log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        return JsonResponse({'code': 0, 'message': 'success', 'data': data})
    except LogEntry.DoesNotExist:
        return JsonResponse({'code': 1, 'message': '日志不存在'}, status=404)


def log_statistics_view(request):
    """日志统计视图"""
    # 时间范围
    days = int(request.GET.get('days', 7))
    start_date = timezone.now() - timedelta(days=days)

    # 按级别统计
    level_stats = LogEntry.objects.filter(
        created_at__gte=start_date
    ).values('level').annotate(
        count=Count('id')
    ).order_by('level')

    # 按 logger 统计
    logger_stats = LogEntry.objects.filter(
        created_at__gte=start_date
    ).values('logger_name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    # 错误趋势（按天）
    error_trend = LogEntry.objects.filter(
        created_at__gte=start_date,
        level__in=['ERROR', 'CRITICAL']
    ).extra(
        select={'day': "DATE(created_at)"}
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')

    return JsonResponse({
        'code': 0,
        'message': 'success',
        'data': {
            'level_stats': list(level_stats),
            'logger_stats': list(logger_stats),
            'error_trend': list(error_trend),
        }
    })


def log_cleanup_view(request):
    """清理旧日志视图"""
    days = int(request.GET.get('days', 30))
    deleted_count, _ = LogEntry.cleanup_old_logs(days=days)
    return JsonResponse({
        'code': 0,
        'message': f'成功清理 {deleted_count} 条日志',
        'data': {'deleted_count': deleted_count}
    })