from rest_framework.pagination import PageNumberPagination
from .response import CustomResponse


class CustomPage(PageNumberPagination):
    page_size = 10
    max_page_size = 100
    page_query_param = 'page'
    page_size_query_param = 'size'

    def get_paginated_response(self, data):
        return CustomResponse(
            data={
                'count': self.page.paginator.count,
                'page': self.page.number,
                'size': self.page_size,
                'list': data
            },
            msg='success', code=201)

    def get_page_size(self, request):
        page_size = request.data.get(self.page_size_query_param, self.page_size)
        self.page_size = page_size
        if page_size is not None:
            return self.page_size
        else:
            return super().get_page_size(request)

    def get_page_number(self, request, paginator):
        page_number = request.data.get(self.page_query_param, 1)
        return page_number
