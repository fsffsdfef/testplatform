import jwt
from config.settings import base


def get_token(request):
    """
    获取token，并解析，无token时，返回None
    @param request: 请求包
    @return: token信息
    """
    token = next(
        (i for i in [request.META.get('HTTP_AUTHORIZATION', '')[7:], request.data.get('token')]
         if i is not None and i != ''), None)
    if token is None:
        return None
    token_info = token_analysis(token)
    return token_info


def token_analysis(token):
    """
    解析token
    """
    key = base.SECRET_KEY
    algorithm = base.ALGORITHM
    token_dict = jwt.decode(token, key=key, algorithms=[algorithm])
    return token_dict
