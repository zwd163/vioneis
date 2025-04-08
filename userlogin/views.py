from django.http import JsonResponse
from utils.fbmsg import FBMsg
from django.contrib import auth
from django.contrib.auth.models import User
import json
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
        user_detail = Users.objects.filter(user_id=user.id).first()
        if user_detail and hasattr(user_detail, 'openid'):
            # Case-insensitive staff name search
            staff_obj = staff.objects.filter(openid=user_detail.openid, staff_name__iexact=str(user.username)).first()
            if staff_obj:
                staff_id = staff_obj.id
            else:
                err_ret = FBMsg.err_ret()
                err_ret['msg'] = 'Invalid username or password'
                err_ret['data'] = data
                return JsonResponse(err_ret, status=status.HTTP_401_UNAUTHORIZED)
        else:
            err_ret = FBMsg.err_ret()
            err_ret['msg'] = 'Invalid username or password'
            err_ret['data'] = data
            return JsonResponse(err_ret, status=status.HTTP_401_UNAUTHORIZED)

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
    # Print debug information
    print("forgot_password function called")
    print("Request method:", request.method)
    print("Request path:", request.path)
    print("Request headers:", request.headers)

    # Simple test response
    return JsonResponse({"code": "200", "msg": "Test response", "data": None})

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
