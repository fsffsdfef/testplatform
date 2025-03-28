from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet
from ..sers.user_jws import *


class TokenView(TokenObtainPairView):
    permission_classes = [AllowAny, ]
    serializer_class = TokenSer


class UserView(ModelViewSet):
    queryset = UserModel.objects.all()
    serializer_class = UserSer
    permission_classes = []
