from django.http import JsonResponse
from utils.fbmsg import FBMsg
from django.contrib import auth
from django.contrib.auth.models import User
import json
from userprofile.models import Users
from staff.models import ListModel as staff
from rest_framework import status
from django.contrib.auth import authenticate

def login(request, *args, **kwargs):
    post_data = json.loads(request.body.decode())
    data = {
        "name": post_data.get('name'),
        "password": post_data.get('password'),
    }
    ip = request.META.get('HTTP_X_FORWARDED_FOR') if request.META.get(
        'HTTP_X_FORWARDED_FOR') else request.META.get('REMOTE_ADDR')
    # --- START CHANGE ---
    # Explanation: Check if the username exists before attempting to authenticate.
    if User.objects.filter(username=str(data['name'])).exists():
        # --- END CHANGE ---
        user = authenticate(request, username=str(data['name']), password=str(data['password']))
        if user is not None:
            auth.login(request, user)
            user_detail = Users.objects.filter(user_id=user.id).first()
            if user_detail and hasattr(user_detail, 'openid'):
                staff_obj = staff.objects.filter(openid=user_detail.openid, staff_name=str(user.username)).first()
                # --- START CHANGE ---
                # Explanation: Check if the staff_obj exists.
                if staff_obj:
                    staff_id = staff_obj.id
                else:
                    err_ret = FBMsg.err_ret()
                    err_ret['msg'] = 'Invalid username or password'
                    err_ret['data'] = data
                    return JsonResponse(err_ret, status=status.HTTP_401_UNAUTHORIZED)
                # --- END CHANGE ---
            else:
                # --- START CHANGE ---
                # Explanation: Return 401 Unauthorized if the user_detail or openid is not found.
                err_ret = FBMsg.err_ret()
                err_ret['msg'] = 'Invalid username or password'
                err_ret['data'] = data
                return JsonResponse(err_ret, status=status.HTTP_401_UNAUTHORIZED)
                # --- END CHANGE ---
            data = {
                "name": data['name'],
                'openid': user_detail.openid,
                "user_id": staff_id
            }
            ret = FBMsg.ret()
            ret['ip'] = ip
            ret['data'] = data
            # --- START CHANGE ---
            # Explanation: Return 200 OK if the login is successful.
            return JsonResponse(ret, status=status.HTTP_200_OK)
            # --- END CHANGE ---
        else:
            # --- START CHANGE ---
            # Explanation: Return 401 Unauthorized if the password is not correct.
            err_ret = FBMsg.err_ret()
            err_ret['msg'] = 'Invalid username or password'
            err_ret['data'] = data
            return JsonResponse(err_ret, status=status.HTTP_401_UNAUTHORIZED)
            # --- END CHANGE ---
    else:
        # --- START CHANGE ---
        # Explanation: Return 401 Unauthorized if the username is not found.
        err_ret = FBMsg.err_ret()
        err_ret['msg'] = 'Invalid username or password'
        err_ret['data'] = data
        return JsonResponse(err_ret, status=status.HTTP_401_UNAUTHORIZED)
        # --- END CHANGE ---
