from userprofile.models import Users
from rest_framework.exceptions import APIException
from rest_framework.authentication import BaseAuthentication
from utils.md5 import Md5

class TokenObject:
    def __init__(self, openid):
        self.openid = openid
        # 根据 openid 生成 appid，与原来的逻辑保持一致
        self.appid = Md5.md5(openid + '1')

class Authtication(BaseAuthentication):
    def authenticate(self, request):
        # 记录请求头部信息进行调试
        print(f"Debug - Auth headers: {request.META}")

        if request.path in ['/api/docs/', '/api/debug/', '/api/']:
            return (False, None)
        else:
            token = request.META.get('HTTP_TOKEN')
            print(f"Debug - Token from header: {token}")

            if token:
                if Users.objects.filter(openid__exact=str(token)).exists():
                    user = Users.objects.filter(openid__exact=str(token)).first()
                    # 创建一个包含 openid 和 appid 的对象，并将其存储在 request.auth 中
                    auth = TokenObject(token)
                    print(f"Debug - Created auth object with openid: {auth.openid}, appid: {auth.appid}")
                    return (user, auth)
                else:
                    raise APIException({"detail": "User Does Not Exists"})
            else:
                # 不抛出异常，而是返回False，让前端处理
                return (None, None)

    def authenticate_header(self, request):
        return 'Token'
