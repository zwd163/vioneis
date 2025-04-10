from django.http import JsonResponse
from utils.fbmsg import FBMsg
from django.contrib import auth
from django.contrib.auth.models import User
import json, random, os
from userprofile.models import Users
from staff.models import ListModel as staff
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.shortcuts import render, redirect
from .models import PasswordResetToken
from utils.email import send_password_reset_email
from django.utils import timezone
from utils.md5 import Md5

def login(request, *args, **kwargs):
    post_data = json.loads(request.body.decode())
    data = {
        "name": post_data.get('name'),
        "password": post_data.get('password'),
    }
    ip = request.META.get('HTTP_X_FORWARDED_FOR') if request.META.get(
        'HTTP_X_FORWARDED_FOR') else request.META.get('REMOTE_ADDR')

    # Case-insensitive username search
    user_obj = User.objects.filter(username__iexact=str(data['name'])).first()
    if user_obj:
        # Use the actual username with correct case for authentication
        actual_username = user_obj.username
        user = authenticate(request, username=actual_username, password=str(data['password']))
    else:
        user = None

    if user is not None:
        auth.login(request, user)

        # 获取用户详情
        user_detail, created = Users.objects.get_or_create(user_id=user.id)

        # 检查用户是否是 Admin
        is_admin = False
        # 添加 is_delete=False 条件，确保被标记为删除的用户无法登录
        staff_obj = staff.objects.filter(staff_name__iexact=str(user.username), is_delete=False).first()
        if not staff_obj:
            # 如果用户在 staff 表中不存在或已被标记为删除，返回错误
            err_ret = FBMsg.err_ret()
            err_ret['msg'] = 'Invalid username or password'
            err_ret['data'] = data
            return JsonResponse(err_ret, status=status.HTTP_401_UNAUTHORIZED)

        is_admin = staff_obj.staff_type == 'Admin'

        # 只有在 Admin 注册时才应该生成新的 openid
        # 如果不是 Admin 且 openid 为空，应该报错
        if not user_detail.openid or user_detail.openid == '':
            if is_admin:
                # 如果是 Admin 且 openid 为空，生成新的 openid
                user_detail.openid = Md5.md5(user.username)
                user_detail.save()
            else:
                # 如果不是 Admin 且 openid 为空，报错
                err_ret = FBMsg.err_ret()
                err_ret['msg'] = 'Staff user must be associated with an Admin'
                err_ret['data'] = data
                return JsonResponse(err_ret, status=status.HTTP_401_UNAUTHORIZED)

        # 不需要再次查询 staff 表，因为我们已经在上面查询过了
        # 并且确保了 staff_obj 不为 None 且 is_delete=False
        # 确保 staff 表中的 openid 与用户的 openid 一致
        if staff_obj.openid != user_detail.openid:
            staff_obj.openid = user_detail.openid
            staff_obj.save()
        staff_id = staff_obj.id

        data = {
            "name": data['name'],
            'openid': user_detail.openid,
            "user_id": staff_id
        }
        ret = FBMsg.ret()
        ret['ip'] = ip
        ret['data'] = data
        return JsonResponse(ret, status=status.HTTP_200_OK)
    else:
        err_ret = FBMsg.err_ret()
        err_ret['msg'] = 'Invalid username or password'
        err_ret['data'] = data
        return JsonResponse(err_ret, status=status.HTTP_401_UNAUTHORIZED)

def test_view(request):
    """
    Test view function
    """
    return JsonResponse({"code": "200", "msg": "Test view response", "data": None})

def refresh_token(request):
    """
    Refresh user token (OPENID) if user is authenticated via session
    """
    if request.method == 'POST':
        # Check if user is authenticated via session
        user_id = request.session.get('user_id')
        if user_id:
            try:
                # Get user from session
                from django.contrib.auth.models import User
                user = User.objects.get(id=user_id)

                # Get or create openid
                from userprofile.models import Users
                user_profile, created = Users.objects.get_or_create(user_id=user_id)
                openid = user_profile.openid

                # Return the openid as token
                return JsonResponse({
                    "code": "200",
                    "msg": "Token refreshed successfully",
                    "data": {"openid": openid}
                })
            except Exception as e:
                print(f"Error refreshing token: {str(e)}")
                return JsonResponse({
                    "code": "400",
                    "msg": "Failed to refresh token",
                    "data": None
                }, status=400)
        else:
            return JsonResponse({
                "code": "401",
                "msg": "User not authenticated",
                "data": None
            }, status=401)
    else:
        return JsonResponse({
            "code": "405",
            "msg": "Method not allowed",
            "data": None
        }, status=405)

def forgot_password(request, *args, **kwargs):
    """
    Handle forgot password request
    """
    if request.method != 'POST':
        return JsonResponse({"code": "405", "msg": "Method not allowed", "data": None}, status=405)

    try:
        post_data = json.loads(request.body.decode())
        username = post_data.get('username')
        email = post_data.get('email')

        # 验证用户名和邮箱
        user = User.objects.filter(username__iexact=username).first()
        if not user:
            return JsonResponse({
                "code": "400",
                "msg": "User name/email not match",
                "data": None
            })

        # 从 staff 表中获取邮箱
        staff_obj = staff.objects.filter(staff_name__iexact=username).first()
        if not staff_obj or not staff_obj.email or staff_obj.email.lower() != email.lower():
            return JsonResponse({
                "code": "400",
                "msg": "User name/email not match",
                "data": None
            })

        # 生成密码重置令牌
        token_obj = PasswordResetToken.objects.create(
            user_id=user.id,
            email=staff_obj.email,
            expires_at=timezone.now() + timezone.timedelta(hours=24)
        )

        # 构建密码重置链接
        reset_link = f"{request.scheme}://{request.get_host()}/reset-password/{token_obj.token}/"

        # 发送密码重置邮件
        email_sent = send_password_reset_email(staff_obj.email, username, reset_link)

        if email_sent:
            return JsonResponse({
                "code": "200",
                "msg": "Password reset email sent",
                "data": None
            })
        else:
            return JsonResponse({
                "code": "500",
                "msg": "Failed to send email",
                "data": None
            })
    except Exception as e:
        print(f"Error in forgot_password: {str(e)}")
        return JsonResponse({
            "code": "500",
            "msg": "Server error",
            "data": None
        })

def reset_password(request, token):
    """
    Handle password reset link
    """
    try:
        # Find token in database
        token_obj = PasswordResetToken.objects.filter(token=token).first()

        if not token_obj or not token_obj.is_valid():
            # Token is invalid or expired
            return render(request, 'password_reset_error.html', {
                'error': 'Invalid or expired password reset link'
            })

        # Redirect to frontend reset password page
        frontend_url = f"/reset-password?token={token}"
        return redirect(frontend_url)

    except Exception as e:
        print(f"Exception in reset_password: {str(e)}")
        return render(request, 'password_reset_error.html', {
            'error': str(e)
        })

def reset_password_confirm(request):
    """
    Handle password reset confirmation
    """
    if request.method != 'POST':
        return JsonResponse({"code": "400", "msg": "Method not allowed", "data": None}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    try:
        post_data = json.loads(request.body.decode())
        print(f"Received reset confirm data: {post_data}")
        token_str = post_data.get('token')
        new_password = post_data.get('new_password')
        confirm_password = post_data.get('confirm_password')

        if not token_str or not new_password or not confirm_password:
            return JsonResponse({"code": "400", "msg": "Token and passwords are required", "data": None}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return JsonResponse({"code": "400", "msg": "Passwords do not match", "data": None}, status=status.HTTP_400_BAD_REQUEST)

        # Find token in database
        token_obj = PasswordResetToken.objects.filter(token=token_str).first()

        if not token_obj or not token_obj.is_valid():
            return JsonResponse({"code": "400", "msg": "Invalid or expired token", "data": None}, status=status.HTTP_400_BAD_REQUEST)

        # Get user
        user = User.objects.filter(id=token_obj.user_id).first()
        if not user:
            return JsonResponse({"code": "400", "msg": "User not found", "data": None}, status=status.HTTP_404_NOT_FOUND)

        # Update password
        user.set_password(new_password)
        user.save()

        # Mark token as used
        token_obj.is_used = True
        token_obj.save()

        return JsonResponse({"code": "200", "msg": "Password reset successful", "data": None}, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Exception in reset_password_confirm: {str(e)}")
        return JsonResponse({"code": "400", "msg": str(e), "data": None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def register(request):
    """Handle user registration"""
    if request.method == 'POST':
        try:
            # Get data from request
            post_data = json.loads(request.body.decode())
            data = {
                "name": post_data.get('name'),
                "email": post_data.get('email'),  # 添加 email 字段
                "password1": post_data.get('password1'),
                "password2": post_data.get('password2'),
            }

            # Get client IP
            ip = request.META.get('HTTP_X_FORWARDED_FOR') if request.META.get('HTTP_X_FORWARDED_FOR') else request.META.get('REMOTE_ADDR')

            # Validate data
            if not data.get('name'):
                err_name_empty = FBMsg.err_name_empty()
                err_name_empty['ip'] = ip
                err_name_empty['data'] = data['name']
                return JsonResponse(err_name_empty)

            if not data.get('password1'):
                err_password1_empty = FBMsg.err_password1_empty()
                err_password1_empty['ip'] = ip
                err_password1_empty['data'] = data['name']
                return JsonResponse(err_password1_empty)

            if not data.get('password2'):
                err_password2_empty = FBMsg.err_password2_empty()
                err_password2_empty['ip'] = ip
                err_password2_empty['data'] = data['name']
                return JsonResponse(err_password2_empty)

            if data['password1'] != data['password2']:
                err_password_not_same = FBMsg.err_password_not_same()
                err_password_not_same['ip'] = ip
                err_password_not_same['data'] = data['name']
                return JsonResponse(err_password_not_same)

            # Check if username already exists
            if User.objects.filter(username=data['name']).exists():
                err_user_same = FBMsg.err_user_same()
                err_user_same['ip'] = ip
                err_user_same['data'] = data['name']
                return JsonResponse(err_user_same)

            # Create user
            transaction_code = Md5.md5(data['name'])
            user = User.objects.create_user(username=str(data['name']), password=str(data['password1']))

            # Create user profile
            Users.objects.create(
                user_id=user.id,
                name=str(data['name']),
                openid=transaction_code,
                appid=Md5.md5(data['name'] + '1'),
                t_code=Md5.md5(str(timezone.now())),
                developer=1,
                ip=ip
            )

            # Login user
            auth.login(request, user)

            # Generate check code (for reference only, not stored in database)
            check_code = random.randint(1000, 9999)

            # 检查是否提供了邮箱
            if not data.get('email'):
                err_email_empty = FBMsg.err_ret()
                err_email_empty['msg'] = 'Email is required'
                err_email_empty['ip'] = ip
                err_email_empty['data'] = data['name']
                return JsonResponse(err_email_empty)

            # Create staff with email
            staff_obj = staff.objects.create(
                staff_name=str(data['name']),
                staff_type='Admin',
                email=str(data['email']),  # 添加 email 字段
                openid=transaction_code
            )

            # Get staff ID
            user_id = staff_obj.id

            # Create media folders
            folder = os.path.exists(os.path.join(settings.BASE_DIR, 'media/' + transaction_code))
            if not folder:
                os.makedirs(os.path.join(settings.BASE_DIR, 'media/' + transaction_code))
                os.makedirs(os.path.join(settings.BASE_DIR, 'media/' + transaction_code + "/win32"))
                os.makedirs(os.path.join(settings.BASE_DIR, 'media/' + transaction_code + "/linux"))
                os.makedirs(os.path.join(settings.BASE_DIR, 'media/' + transaction_code + "/darwin"))

            # Return success response
            ret = FBMsg.ret()
            ret['ip'] = ip
            data['openid'] = transaction_code
            data['name'] = str(data['name'])
            data['user_id'] = user_id
            data.pop('password1', '')
            data.pop('password2', '')
            ret['data'] = data
            return JsonResponse(ret)

        except Exception as e:
            print(f"Error in register: {str(e)}")
            return JsonResponse({"code": "500", "msg": "Server error", "data": None}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return JsonResponse({"code": "405", "msg": "Method not allowed", "data": None}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
