from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from utils.baseresponse import BaseResponse
from django.http import Http404
from django.shortcuts import get_object_or_404 as _get_object_or_404
from django.core.exceptions import ValidationError


def get_object_or_404(queryset, *filter_args, **filter_kwargs):
    """
    Same as Django's standard shortcut, but make sure to also raise 404
    if the filter_kwargs don't match the required types.
    """
    try:
        return _get_object_or_404(queryset, *filter_args, **filter_kwargs)
    except (TypeError, ValueError, ValidationError):
        raise Http404


class CustomView(ModelViewSet):

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return BaseResponse(data=serializer.data, status=status.HTTP_201_CREATED, headers=headers, msg='OK')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return BaseResponse(data=serializer.data, status=status.HTTP_201_CREATED, msg='ok')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return BaseResponse(data=serializer.data, status=status.HTTP_201_CREATED, msg='ok')

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return BaseResponse(data=serializer.data, status=status.HTTP_201_CREATED, msg='ok')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return BaseResponse(data={}, status=status.HTTP_204_NO_CONTENT, msg='ok')

    # def get_object(self):
    #
    #     queryset = self.filter_queryset(self.get_queryset())
    #
    #     pk = self.request.data.get('pk')
    #     print(f'pkkk: {pk}')
    #
    #     assert pk is not None, (
    #             'Expected view %s to be called with a query parameter '
    #             'named "pk". Fix your request, or set the `.lookup_field` '
    #             'attribute on the view correctly.' % self.__class__.__name__
    #     )
    #
    #     filter_kwargs = {self.lookup_field: pk}
    #     obj = get_object_or_404(queryset, **filter_kwargs)
    #
    #     self.check_object_permissions(self.request, obj)
    #
    #     return obj
