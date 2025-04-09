from django.http import StreamingHttpResponse, JsonResponse, HttpResponse
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from wsgiref.util import FileWrapper
from rest_framework.exceptions import APIException
import mimetypes, os

def robots(request):
    path = settings.BASE_DIR + request.path_info
    content_type, encoding = mimetypes.guess_type(path)
    resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')), content_type=content_type)
    resp['Cache-Control'] = "max-age=864000000000"
    return resp

def favicon(request):
    path = str(settings.BASE_DIR) + '/static/img/logo.png'
    content_type, encoding = mimetypes.guess_type(path)
    resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')), content_type=content_type)
    resp['Cache-Control'] = "max-age=864000000000"
    return resp

def css(request):
    path = str(settings.BASE_DIR) + '/templates/dist/spa' + request.path_info
    content_type, encoding = mimetypes.guess_type(path)
    resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')), content_type=content_type)
    resp['Cache-Control'] = "max-age=864000000000"
    return resp

def js(request):
    path = str(settings.BASE_DIR) + '/templates/dist/spa' + request.path_info
    content_type, encoding = mimetypes.guess_type(path)
    resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')), content_type=content_type)
    resp['Cache-Control'] = "max-age=864000000000"
    return resp

def statics(request):
    path = str(settings.BASE_DIR) + '/templates/dist/spa' + request.path_info
    content_type, encoding = mimetypes.guess_type(path)
    resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')), content_type=content_type)
    resp['Cache-Control'] = "max-age=864000000000"
    return resp

def fonts(request):
    path = str(settings.BASE_DIR) + '/templates/dist/spa' + request.path_info
    content_type, encoding = mimetypes.guess_type(path)
    resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')), content_type=content_type)
    resp['Cache-Control'] = "max-age=864000000000"
    return resp

def myip(request):
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    print(s.getsockname()[0])
    ip = s.getsockname()[0]
    s.close()
    return JsonResponse({"ip": ip})

def reset_password_view(request):
    """
    Handle password reset requests
    """
    token = request.GET.get('token')
    if not token:
        return HttpResponse("Invalid password reset link. No token provided.")

    try:
        user_id = int(token)
        user = User.objects.get(id=user_id)
        # 检查用户是否存在于 staff 表中
        from staff.models import ListModel as StaffModel
        staff_obj = StaffModel.objects.filter(staff_name=user.username).first()
        if not staff_obj:
            return HttpResponse(f"User {user.username} not found in staff table.")
    except (ValueError, User.DoesNotExist):
        return HttpResponse("Invalid password reset link. User not found.")

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not password or not confirm_password:
            return render(request, 'reset_password.html', {
                'error': 'Please enter both password fields',
                'token': token
            })

        if password != confirm_password:
            return render(request, 'reset_password.html', {
                'error': 'Passwords do not match',
                'token': token
            })

        if len(password) < 4:  # 将密码长度要求从 8 降低到 4
            return render(request, 'reset_password.html', {
                'error': 'Password must be at least 4 characters long',
                'token': token
            })

        try:
            # 设置新密码
            user.set_password(password)
            user.save()

            # 更新用户的 openid
            from userprofile.models import Users
            user_profile = Users.objects.filter(user_id=user.id).first()
            if user_profile:
                from utils.md5 import Md5
                # 更新 openid
                user_profile.openid = Md5.md5(user.username)
                user_profile.save()

                # 更新 staff 表中的 openid
                if staff_obj:
                    staff_obj.openid = user_profile.openid
                    staff_obj.save()

            return render(request, 'reset_password_success.html')
        except Exception as e:
            import traceback
            traceback.print_exc()
            return render(request, 'reset_password.html', {
                'error': f'Error setting password: {str(e)}',
                'token': token
            })

    return render(request, 'reset_password.html', {'token': token})
