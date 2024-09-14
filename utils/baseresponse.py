from collections import OrderedDict
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.serializers import Serializer


class BaseResponse(Response):
    """自定义接口返回数据结构"""
    def __init__(self, data=None, status=None, msg=None, code=None,
                 template_name=None, headers=None,
                 exception=False, content_type=None, **kwargs):
        super().__init__(None, status=status)

        if isinstance(data, Serializer):
            msg = (
                'You passed a Serializer instance as data, but '
                'probably meant to pass serialized `.data` or '
                '`.error`. representation.'
            )
            raise AssertionError(msg)

        self.data = {'data': data, 'msg': msg, 'code': code, 'status': status}
        self.data.update(kwargs)
        self.template_name = template_name
        self.exception = exception
        self.content_type = content_type

        if headers:
            for name, value in headers.items():
                self[name] = value


class BasePage(PageNumberPagination):

    page_size = 5
    max_page_size = 10
    page_size_query_param = 'size'
    page_query_param = 'page'
    page_number = None
    total_page = None
    total = count = None

    def get_page_number(self, request, paginator):
        if request.data:
            return request.data.get(self.page_query_param, 1)
        return super().get_page_number(request, paginator)

    def get_page_size(self, request):
        if request.data:
            return request.data.get(self.page_size_query_param, self.page_size)
        return super().get_page_size(request)

    def get_paginated_response(self, data):
        return BaseResponse(data=OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('list', data)
        ]))
