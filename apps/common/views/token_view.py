from rest_framework_simplejwt.views import TokenObtainPairView
from ..sers.customtoken import CustomTokenSer
from rest_framework.permissions import AllowAny


class MyObtainTokenPairView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = CustomTokenSer
