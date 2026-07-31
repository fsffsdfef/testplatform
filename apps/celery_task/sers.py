import json
import re

from rest_framework import serializers
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.utils import timezone as dj_timezone
from django_celery_beat.models import (
    PeriodicTask,
    PeriodicTasks,
    IntervalSchedule,
    ClockedSchedule,
    SolarSchedule,
    CrontabSchedule,
)


def _parse_json_text(value, default, field_name):
    """PeriodicTask.args / kwargs 在库里是 JSON 字符串"""
    if value is None or value == '':
        return json.dumps(default)
    if isinstance(value, (list, dict)):
        return json.dumps(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return json.dumps(default)
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise serializers.ValidationError(f'{field_name} JSON 格式错误: {exc}')
        return json.dumps(parsed)
    return json.dumps(value)


def _normalize_dt(value):
    if value is None or value == '':
        return None
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if ' ' in text and 'T' not in text:
            text = text.replace(' ', 'T', 1)
        dt = parse_datetime(text)
    else:
        dt = value
    if dt and dj_timezone.is_naive(dt):
        dt = dj_timezone.make_aware(dt, dj_timezone.get_current_timezone())
    return dt


def _parse_run_time(run_time):
    if not run_time:
        return '9', '0'
    text = str(run_time).strip()
    if re.match(r'^\d{1,2}:\d{2}(:\d{2})?$', text):
        hour, minute = text.split(':')[:2]
        return str(int(hour)), str(int(minute))
    dt = _normalize_dt(text)
    if dt:
        return str(dt.hour), str(dt.minute)
    return '9', '0'


def _get_or_create_crontab(minute, hour, day_of_week, day_of_month, month_of_year):
    tz = getattr(settings, 'CELERY_TIMEZONE', settings.TIME_ZONE)
    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute=str(minute),
        hour=str(hour),
        day_of_week=str(day_of_week),
        day_of_month=str(day_of_month),
        month_of_year=str(month_of_year),
        timezone=tz,
    )
    return schedule


def _build_crontab_from_run_cycle(raw):
    run_type = raw.get('runCycleType') or 'daily'

    if run_type == 'custom':
        expr = str(raw.get('cronExpression') or '').strip()
        parts = expr.split()
        if len(parts) != 5:
            raise serializers.ValidationError({
                'cronExpression': 'Cron 表达式必须是 5 段，例如：0 9 * * *'
            })
        minute, hour, day_of_month, month_of_year, day_of_week = parts
        return _get_or_create_crontab(minute, hour, day_of_week, day_of_month, month_of_year)

    hour, minute = _parse_run_time(raw.get('runTime'))
    day_of_week = '*'
    day_of_month = '*'
    month_of_year = '*'

    if run_type == 'weekly':
        day_of_week = str(raw.get('runWeekDay') or '').strip()
        if not day_of_week:
            raise serializers.ValidationError({'runWeekDay': '请选择运行日'})
    elif run_type == 'monthly':
        day_of_month = str(raw.get('runMonthDay') or '').strip()
        if not day_of_month:
            raise serializers.ValidationError({'runMonthDay': '请选择运行日期'})
    elif run_type != 'daily':
        raise serializers.ValidationError({'runCycleType': '无效的运行周期类型'})

    return _get_or_create_crontab(minute, hour, day_of_week, day_of_month, month_of_year)


def _is_simple_number(value):
    return str(value).isdigit()


def _format_run_time(hour, minute):
    if _is_simple_number(hour) and _is_simple_number(minute):
        return f'{int(hour):02d}:{int(minute):02d}:00'
    return '09:00:00'

WEEK_DAY_LABEL = {
    '0': '周日',
    '1': '周一',
    '2': '周二',
    '3': '周三',
    '4': '周四',
    '5': '周五',
    '6': '周六',
}

RUN_CYCLE_LABEL = {
    'daily': '每天',
    'weekly': '每周',
    'monthly': '每月',
    'custom': '自定义',
}


def _format_run_time_short(run_time):
    text = str(run_time or '09:00:00')
    if re.match(r'^\d{1,2}:\d{2}', text):
        return text[:5]
    return text

def _crontab_to_form_data(c):
    minute = str(c.minute)
    hour = str(c.hour)
    day_of_week = str(c.day_of_week)
    day_of_month = str(c.day_of_month)
    month_of_year = str(c.month_of_year)
    run_time = _format_run_time(hour, minute)
    cron_expression = f'{minute} {hour} {day_of_month} {month_of_year} {day_of_week}'

    has_complex = any(
        (not _is_simple_number(v) and v != '*')
        for v in [minute, hour, day_of_week, day_of_month, month_of_year]
    )

    if has_complex:
        return {
            'runCycleType': 'custom',
            'runTime': run_time,
            'runWeekDay': '1',
            'runMonthDay': '1',
            'cronExpression': cron_expression,
        }

    if day_of_week != '*' and day_of_month == '*' and month_of_year == '*':
        return {
            'runCycleType': 'weekly',
            'runTime': run_time,
            'runWeekDay': day_of_week,
            'runMonthDay': '1',
            'cronExpression': cron_expression,
        }

    if day_of_month != '*' and day_of_week == '*' and month_of_year == '*':
        return {
            'runCycleType': 'monthly',
            'runTime': run_time,
            'runWeekDay': '1',
            'runMonthDay': day_of_month,
            'cronExpression': cron_expression,
        }

    if day_of_week == '*' and day_of_month == '*' and month_of_year == '*':
        return {
            'runCycleType': 'daily',
            'runTime': run_time,
            'runWeekDay': '1',
            'runMonthDay': '1',
            'cronExpression': cron_expression,
        }

    return {
        'runCycleType': 'custom',
        'runTime': run_time,
        'runWeekDay': '1',
        'runMonthDay': '1',
        'cronExpression': cron_expression,
    }


class PeriodicTaskSer(serializers.ModelSerializer):
    schedule = serializers.SerializerMethodField(method_name='_get_schedule', read_only=True)

    runCycleType = serializers.CharField(required=False, write_only=True)
    runTime = serializers.CharField(required=False, write_only=True, allow_blank=True)
    runWeekDay = serializers.CharField(required=False, write_only=True, allow_blank=True)
    runMonthDay = serializers.CharField(required=False, write_only=True, allow_blank=True)
    cronExpression = serializers.CharField(required=False, write_only=True, allow_blank=True)

    cronMinute = serializers.CharField(required=False, write_only=True)
    cronHour = serializers.CharField(required=False, write_only=True)
    cronDayOfWeek = serializers.CharField(required=False, write_only=True)
    cronDayOfMonth = serializers.CharField(required=False, write_only=True)
    cronMonthOfYear = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = PeriodicTask
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.crontab_id:
            form_data = _crontab_to_form_data(instance.crontab)
            data.update(form_data)
            data['cronMinute'] = instance.crontab.minute
            data['cronHour'] = instance.crontab.hour
            data['cronDayOfWeek'] = instance.crontab.day_of_week
            data['cronDayOfMonth'] = instance.crontab.day_of_month
            data['cronMonthOfYear'] = instance.crontab.month_of_year
        elif instance.interval_id:
            data['runCycleType'] = 'interval'
            data['intervalDesc'] = str(instance.interval)
        return data

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = dict(data)
            data.pop('updateUser', None)
            data.pop('schedule', None)
            for field in ('args', 'kwargs', 'headers'):
                if field in data and isinstance(data[field], (list, dict)):
                    data[field] = json.dumps(data[field], ensure_ascii=False)
            if 'start_time' in data:
                data['start_time'] = _normalize_dt(data.get('start_time'))
            if 'expires' in data:
                data['expires'] = _normalize_dt(data.get('expires'))
        return super().to_internal_value(data)

    def validate(self, attrs):
        raw = getattr(self, 'initial_data', {}) or {}

        if raw.get('cronMinute') is not None:
            attrs['crontab'] = _get_or_create_crontab(
                raw.get('cronMinute', '0'),
                raw.get('cronHour', '*'),
                raw.get('cronDayOfWeek', '*'),
                raw.get('cronDayOfMonth', '*'),
                raw.get('cronMonthOfYear', '*'),
            )
        else:
            attrs['crontab'] = _build_crontab_from_run_cycle(raw)

        attrs['interval'] = None
        attrs['clocked'] = None
        attrs['solar'] = None

        if not attrs.get('crontab'):
            raise serializers.ValidationError('请设置运行周期')

        for field in (
            'runCycleType', 'runTime', 'runWeekDay', 'runMonthDay', 'cronExpression',
            'cronMinute', 'cronHour', 'cronDayOfWeek', 'cronDayOfMonth', 'cronMonthOfYear',
        ):
            attrs.pop(field, None)

        return attrs

    @staticmethod
    def _get_schedule(obj):
        if obj.crontab_id:
            form_data = _crontab_to_form_data(obj.crontab)
            cycle_type = form_data.get('runCycleType', 'custom')
            run_time = _format_run_time_short(form_data.get('runTime'))

            if cycle_type == 'daily':
                return f'每天 {run_time}'

            if cycle_type == 'weekly':
                week_val = str(form_data.get('runWeekDay', '1'))
                week_label = WEEK_DAY_LABEL.get(week_val, f'周{week_val}')
                return f'每周 {week_label} {run_time}'

            if cycle_type == 'monthly':
                return f'每月 {form_data.get("runMonthDay")}日 {run_time}'

            return f'自定义 {form_data.get("cronExpression", "")}'

        if obj.interval_id:
            interval_text = str(obj.interval)
            interval_label_map = {
                'every day': '每 1 天',
                'every hour': '每 1 小时',
                'every minute': '每 1 分钟',
                'every second': '每 1 秒',
            }
            label = interval_label_map.get(interval_text, interval_text)
            return f'固定间隔 {label}'

        if obj.clocked_id:
            return f'指定时间 {obj.clocked.clocked_time}'

        if obj.solar_id:
            return str(obj.solar)

        return ''

    def validate_args(self, value):
        text = _parse_json_text(value, [], 'args')
        parsed = json.loads(text)
        if not isinstance(parsed, list):
            raise serializers.ValidationError('args 必须是 JSON 数组，例如 [1001] 或 [[1001,1002]]')
        return text

    def validate_kwargs(self, value):
        text = _parse_json_text(value, {}, 'kwargs')
        parsed = json.loads(text)
        if not isinstance(parsed, dict):
            raise serializers.ValidationError('kwargs 必须是 JSON 对象')
        return text

    def validate_headers(self, value):
        return _parse_json_text(value, {}, 'headers')


class PeriodicTasksSer(serializers.ModelSerializer):

    class Meta:
        model = PeriodicTasks
        fields = '__all__'


class IntervalScheduleSer(serializers.ModelSerializer):
    intervalName = serializers.SerializerMethodField(method_name='_get_interval_name')

    class Meta:
        model = IntervalSchedule
        fields = '__all__'

    @staticmethod
    def _get_interval_name(obj):
        return f'{str(obj.every)} {obj.period}'


class ClockedScheduleSer(serializers.ModelSerializer):

    class Meta:
        model = ClockedSchedule
        fields = '__all__'


class SolarScheduleSer(serializers.ModelSerializer):

    class Meta:
        model = SolarSchedule
        fields = '__all__'


class CrontabScheduleSer(serializers.ModelSerializer):

    class Meta:
        model = CrontabSchedule
        exclude = ['timezone']