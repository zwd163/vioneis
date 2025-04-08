from userprofile.models import Users
from rest_framework.exceptions import APIException

class Authtication(object):
    def authenticate(self, request):
        if request.path in ['/api/docs/', '/api/debug/', '/api/']:
            return (False, None)
        else:
            token = request.META.get('HTTP_TOKEN')
            if token:
                if Users.objects.filter(openid__exact=str(token)).exists():
                    user = Users.objects.filter(openid__exact=str(token)).first()
                    return (True, user)
                else:
                    raise APIException({"detail": "User Does Not Exists"})
            else:
                # 不抛出异常，而是返回False，让前端处理
                return (False, None)

    def authenticate_header(self, request):
        pass
