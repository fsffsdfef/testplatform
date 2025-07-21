from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from rest_framework.generics import GenericAPIView
from commons.cusntom.response import CustomResponse
from django.db.models import Q
from commons.cusntom.pagination import CustomPage
from commons.cusntom.view import CustomView
from ..sers.user_jws import *


class TokenView(TokenObtainPairView):
    permission_classes = [AllowAny, ]
    serializer_class = TokenSer


class UserView(CustomView):
    model = UserModel
    serializer_class = UserSer
    permission_classes = []
    pagination_class = CustomPage
    fields = {
        "userId": {
            "type": 'exact',
            "converter": int,
            "allow_empty": False
        },
        "email": {
            "type": 'exact',
            "converter": str,
            "allow_empty": False
        },
        "userName": {
            "type": 'icontains',
            "converter": str,
            "allow_empty": True
        },
        "phone": {
            "type": 'exact',
            "converter": str,
            "allow_empty": True
        },
    }
    index_key = 'userId'


user_view = UserView.as_view()
