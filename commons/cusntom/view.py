from django.db.models import Q
from urllib.parse import urlparse
from rest_framework.generics import GenericAPIView
from commons.cusntom.response import CustomResponse
from commons.utils.batch_util import UniversalBatchOperator


class CustomView(GenericAPIView):

    model = None
    fields = None
    index_key = None

    def post(self, request, *args, **kwargs):
        path_handlers = {
            'add': self.add,
            'update': self.update,
            'del': self.delete,
            'getPageList': self.get_query,
            'batch': self.batch
        }
        path = self.get_last_path_segment(request.path)
        action = path_handlers.get(str(path), None)
        if action is not None:
            return action(request=request.data, *args, **kwargs)

    def add(self, request, *args, **kwargs):
        ser = self.serializer_class(data=request)
        if ser.is_valid(raise_exception=True):
            ser.save()
            return CustomResponse(data=ser.data, msg="新建成功", code=101)

    def delete(self, request, *args, **kwargs):
        # 支持单个删除和批量删除
        single_id = request.get(self.index_key)

        batch_ids = request.get('ids', [])  # 批量删除的ID列表
        
        if single_id is not None:
            # 单个删除
            obj = {
                self.index_key: single_id
            }
            try:
                self.model.objects.get(**obj).delete()
                return CustomResponse(data=[], msg="删除成功", code=201)
            except self.model.DoesNotExist:
                return CustomResponse(data=[], msg="记录不存在", code=1001)
        elif batch_ids:
            # 批量删除
            if not isinstance(batch_ids, list):
                return CustomResponse(data=[], msg="批量删除参数格式错误，应为ID列表", code=1001)
            
            if not batch_ids:
                return CustomResponse(data=[], msg="批量删除ID列表为空", code=1001)
            
            try:
                # 使用 filter 和 delete 进行批量删除
                deleted_count, _ = self.model.objects.filter(**{f"{self.index_key}__in": batch_ids}).delete()
                if deleted_count > 0:
                    return CustomResponse(data=[], msg=f"批量删除成功，共删除{deleted_count}条记录", code=201)
                else:
                    return CustomResponse(data=[], msg="未找到要删除的记录", code=1001)
            except Exception as e:
                return CustomResponse(data=[], msg=f"批量删除失败: {str(e)}", code=1001)
        else:
            return CustomResponse(data=[], msg="删除参数为空", code=1001)

    def update(self, request, *args, **kwargs):
        key = request.pop(self.index_key, None)
        model_obj = self.model.objects.get(pk=key)
        ser = self.serializer_class(instance=model_obj, data=request)
        if ser.is_valid(raise_exception=True):  # 校验数据是否满足条件
            ser.save()
            return CustomResponse(data=ser.data, msg="修改成功", code=1004)
        return CustomResponse(data=[], msg="修改失败", code=1004)

    def batch(self, request, *args, **kwargs):
        action_type = request.get("action")
        data = request.get("data", [])
        if len(data) < 1:
            return CustomResponse(data=[], msg="入参为空")
        msg = UniversalBatchOperator(model_class=self.model,
                                     primary_data=data,
                                     primary_key_field=self.index_key,
                                     action_type=action_type).batch()
        return CustomResponse(data=[], **msg)

    def get_query(self, request, *args, **kwargs):
        query_params = {}
        for i in self.fields:
            value = request.get(i, None)
            if value is not None:
                query_params[i] = value
        q_objects = Q()
        processed_fields = set()
        select_related_fields = set()

        for param, value in query_params.items():
            field = param
            lookup_type = self.fields[param].get('type')
            is_range_param = False
            # 处理关联字段
            is_related_field = False
            related_field_path = None
            for base_field, config in self.fields.items():
                if 'param_suffixes' in config and any(param.endswith(suffix) for suffix in config['param_suffixes']):
                    field = base_field
                    lookup_type = 'range' if param.endswith('_start') or param.endswith('_end') else config['type']
                    is_range_param = True
                    break
                # 检查是否是关联字段
                if 'related_field' in config and param == base_field:
                    is_related_field = True
                    related_field_path = config['related_field']
                    related_lookup_type = config.get('related_lookup_type', lookup_type)
                    # 收集需要预加载的关联字段
                    if '__' in related_field_path:
                        select_related_fields.add(related_field_path.split('__')[0])
                    break
            config = self.fields[field]
            converter = config.get('converter')
            allow_empty = config.get('allow_empty', False)
            if not allow_empty and (value is None or str(value).strip() == ''):
                continue
            try:
                if converter:
                    processed_value = converter(value)
                else:
                    processed_value = value
            except (ValueError, TypeError):
                continue

                # 构建查询表达式
            if is_related_field:
                # 时间范围类型
                if is_range_param:
                    if param.endswith('_start'):
                        lookup_expr = f'{related_field_path}__gte'
                    elif param.endswith('_end'):
                        lookup_expr = f'{related_field_path}__lte'
                    else:
                        lookup_expr = f'{related_field_path}__{related_lookup_type}'
                # 非时间类型
                else:
                    lookup_expr = f"{related_field_path}__{related_lookup_type}"
                    print(f'关联字段：{lookup_expr}')
            else:
                # 普通字段查询
                if is_range_param:
                    if param.endswith('_start'):
                        lookup_expr = f'{field}__gte'
                    elif param.endswith('_end'):
                        lookup_expr = f'{field}__lte'
                    else:
                        lookup_expr = f'{field}__{lookup_type}'
                else:
                    lookup_expr = f"{field}__{lookup_type}"

            q_objects &= Q(**{lookup_expr: processed_value})
            processed_fields.add(field)

        queryset = self.model.objects.all()
        # 添加 select_related 优化
        if select_related_fields:
            queryset = queryset.select_related(*select_related_fields)

        if _ := q_objects.children:
            queryset = queryset.filter(q_objects)
        ordered_queryset = queryset.order_by("-updatedDate")
        page_data = self.paginate_queryset(ordered_queryset)
        if page_data is not None:
            serializer = self.serializer_class(instance=page_data, many=True)
            return self.get_paginated_response(serializer.data)
        ser = self.serializer_class(instance=ordered_queryset, many=True)
        return CustomResponse(data=ser.data)

    @staticmethod
    def get_last_path_segment(path):
        parsed = urlparse(path)
        # 分割路径并过滤空字符串
        path_segments = [seg for seg in parsed.path.split('/') if seg]
        return path_segments[-1] if path_segments else None
