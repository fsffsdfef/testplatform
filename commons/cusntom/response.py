from rest_framework.response import Response
from rest_framework.serializers import Serializer


class CustomResponse(Response):

    def __init__(self, data=None, status=None, msg=None, code=None,
                 template_name=None, headers=None,
                 exception=False, content_type=None, success=True, *args, **kwargs):
        super().__init__(None, status=status)

        if isinstance(data, Serializer):
            msg = (
                'You passed a Serializer instance as data, but '
                'probably meant to pass serialized `.data` or '
                '`.error`. representation.'
            )
            raise AssertionError(msg)

        self.data = {'data': data, 'msg': msg, 'code': code, 'success': success}
        self.template_name = template_name
        self.exception = exception
        self.content_type = content_type

        if headers:
            for name, value in headers.items():
                self[name] = value
