from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class CustomTokenSer(TokenObtainSerializer):
    token_class = RefreshToken

    @classmethod
    def get_token(cls, user):

        token = super().get_token(user)
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['token'] = str(refresh.access_token)
        data['expire'] = str(refresh.access_token.payload['exp'])
        return data
