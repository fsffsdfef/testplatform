from django.db.models import Q
from urllib.parse import urlparse
from rest_framework.generics import GenericAPIView
from commons.cusntom.response import CustomResponse


class CustomView(GenericAPIView):

    model = None
    fields = None
    index_key = None

    def post(self, request, *args, **kwargs):
        path_handlers = {
            'add': self.add,
            'update': self.update,
            'del': self.delete,
            'getPageList': self.get_query
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
        obj = {
            self.index_key: request.get(self.index_key)
        }
        if obj[self.index_key] is None:
            return CustomResponse(data=[], msg="ID为空", code=1001)
        self.model.objects.get(**obj).delete()
        return CustomResponse(data=[], msg="删除成功", code=201)

    def update(self, request, *args, **kwargs):
        key = request.pop(self.index_key, None)
        model_obj = self.model.objects.get(pk=key)
        ser = self.serializer_class(instance=model_obj, data=request)
        if ser.is_valid(raise_exception=True):  # 校验数据是否满足条件
            ser.save()
            return CustomResponse(data=ser.data, msg="修改成功", code=1004)
        return CustomResponse(data=[], msg="修改失败", code=1004)

    def get_query(self, request, *args, **kwargs):
        query_params = {}
        for i in self.fields:
            value = request.get(i, None)
            if value is not None:
                query_params[i] = value
        q_objects = Q()
        processed_fields = set()

        for param, value in query_params.items():
            field = param
            lookup_type = self.fields[param].get('type')
            is_range_param = False
            for base_field, config in self.fields.items():
                if 'param_suffixes' in config and any(param.endswith(suffix) for suffix in config['param_suffixes']):
                    field = base_field
                    lookup_type = 'range' if param.endswith('_start') or param.endswith('_end') else config['type']
                    is_range_param = True
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

            if is_range_param:
                if param.endswith('_start'):
                    lookup_expr = f'{field}__gte'
                elif param.endswith('_end'):
                    lookup_expr = f'{field}__lte'
                else:
                    lookup_expr = f'{field}__{lookup_type}'
                q_objects &= Q(**{lookup_expr: processed_value})
            else:
                lookup_expr = f"{field}__{lookup_type}"
                q_objects &= Q(**{lookup_expr: processed_value})
                processed_fields.add(field)

        queryset = self.model.objects.all()
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
