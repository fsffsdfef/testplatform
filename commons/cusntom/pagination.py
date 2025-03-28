from rest_framework.pagination import PageNumberPagination
from .response import CustomResponse


class CustomPage(PageNumberPagination):
    page_size = 5
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
