from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTBodyAuthentication(JWTAuthentication):

    def authenticate(self, request):
        token = request.data.get('token', None)
        if token:
            validated_token = self.get_validated_token(token)
            return self.get_user(validated_token), validated_token
        else:
            return super().authenticate(request)