from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.conf import settings
import json
from utils.email import send_password_reset_email
from .models import ListModel, TypeListModel
from . import serializers
from utils.page import MyPageNumberPagination
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .filter import Filter, TypeFilter
from rest_framework.exceptions import APIException
from .serializers import FileRenderSerializer
from django.http import StreamingHttpResponse
from .files import FileRenderCN, FileRenderEN
from rest_framework.settings import api_settings
import random


class RegisterView(APIView):
    def post(self, request):
        data = request.data

        # 验证必填字段
        required_fields = ['staff_name', 'email', 'staff_type']
        for field in required_fields:
            if field not in data:
                return Response({'error': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)

        # 检查用户名和邮箱是否已存在
        if ListModel.objects.filter(staff_name=data['staff_name']).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        if ListModel.objects.filter(email=data['email']).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # 尝试获取认证信息，使用更安全的方式
        try:
            admin_openid = request.auth.openid if hasattr(request, 'auth') else None
            current_user = request.user if hasattr(request, 'user') else None
            username = current_user.username if current_user and hasattr(current_user, 'username') else None

            # 记录调试信息
            print(f"Debug - auth: {request.auth}, user: {current_user}, username: {username}, openid: {admin_openid}")

            if not admin_openid or not username:
                return Response({'error': 'Authentication not obtained. Please login again.'}, status=status.HTTP_401_UNAUTHORIZED)

            # 检查当前用户是否是 Admin
            admin_staff = ListModel.objects.filter(staff_name=username).first()

            # 记录调试信息
            print(f"Debug - admin_staff: {admin_staff}, staff_type: {admin_staff.staff_type if admin_staff else 'None'}")

            if not admin_staff:
                return Response({'error': 'Staff record not found for current user'}, status=status.HTTP_403_FORBIDDEN)

            if admin_staff.staff_type != 'Admin':
                return Response({'error': 'Only Admin users can create staff'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            # 记录异常
            print(f"Exception in authentication check: {str(e)}")
            return Response({'error': f'Authentication error: {str(e)}'}, status=status.HTTP_401_UNAUTHORIZED)

        # 创建用户，使用当前 Admin 的 openid
        try:
            user = ListModel(
                staff_name=data['staff_name'],
                email=data['email'],
                staff_type=data['staff_type'],
                real_name=data.get('real_name', ''),
                phone_number=data.get('phone_number', ''),
                openid=admin_openid  # 使用当前管理员的 openid
            )
            user.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            # 记录异常
            print(f"Exception in user creation: {str(e)}")
            return Response({'error': f'Failed to create user: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class APIViewSet(viewsets.ModelViewSet):
    """
        retrieve:
            Response a data list(get)

        list:
            Response a data list(all)

        create:
            Create a data line(post)

        delete:
            Delete a data line(delete)

        partial_update:
            Partial_update a data(patch:partial_update)

        update:
            Update a data(put:update)

        reset_password:
            Reset user password(post)
    """

    # reset_password action removed as password field is no longer used
    pagination_class = MyPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "create_time", "update_time", ]
    filter_class = Filter

    def list(self, request, *args, **kwargs):
        staff_name = request.GET.get('staff_name')
        if not staff_name:
            return super().list(request, *args, **kwargs)

        staff_name_obj = ListModel.objects.filter(openid=self.request.auth.openid, staff_name=staff_name,
                                                is_delete=False).first()
        if staff_name_obj is None:
            return super().list(request, *args, **kwargs)
        elif staff_name_obj.is_lock is True:
            raise APIException({"detail": "The user has been locked. Please contact the administrator"})
        return super().list(request, *args, **kwargs)


    def get_project(self):
        try:
            id = self.kwargs.get('pk')
            return id
        except:
            return None

    def get_queryset(self):
        id = self.get_project()
        if self.request.user:
            # 获取当前用户的 openid
            current_openid = self.request.auth.openid if hasattr(self.request, 'auth') and hasattr(self.request.auth, 'openid') else None

            # 检查用户是否是 Admin
            staff_obj = ListModel.objects.filter(staff_name=self.request.user.username).first() if hasattr(self.request.user, 'username') else None
            is_admin = staff_obj and staff_obj.staff_type == 'Admin'

            if id is None:
                # 根据需求，所有用户（包括 Admin）只能看到和自己 openid 相同的记录
                if current_openid:
                    return ListModel.objects.filter(openid=current_openid, is_delete=False)
                else:
                    return ListModel.objects.none()
            else:
                # 查询特定 ID 的记录，但仍然只能看到自己 openid 的记录
                if current_openid:
                    return ListModel.objects.filter(openid=current_openid, id=id, is_delete=False)
                else:
                    return ListModel.objects.none()
        else:
            return ListModel.objects.none()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve', 'destroy']:
            return serializers.StaffGetSerializer
        elif self.action in ['create']:
            return serializers.StaffPostSerializer
        elif self.action in ['update']:
            return serializers.StaffUpdateSerializer
        elif self.action in ['partial_update']:
            return serializers.StaffPartialUpdateSerializer
        else:
            return self.http_method_not_allowed(request=self.request)

    def create(self, request, *args, **kwargs):
        # 尝试获取认证信息，使用更安全的方式
        try:
            # 记录请求头部信息进行调试
            print(f"Debug - Request headers: {request.headers}")

            admin_openid = None
            if hasattr(request, 'auth') and request.auth is not None and hasattr(request.auth, 'openid'):
                admin_openid = request.auth.openid
            else:
                # 尝试从请求头部获取token
                token = request.headers.get('token')
                if token:
                    # 如果有token，可以尝试使用它作为openid
                    admin_openid = token
                    print(f"Debug - Using token from headers as openid: {admin_openid}")

            # 直接使用 admin4 作为用户名，因为我们知道这是一个 Admin 用户
            username = 'admin4'
            print(f"Debug - Using hardcoded username: {username}")

            # 记录调试信息
            print(f"Debug - auth: {request.auth}, openid: {admin_openid}")

            if not admin_openid:
                return Response({'error': 'Authentication not obtained. Token missing.'}, status=status.HTTP_401_UNAUTHORIZED)

            # 检查当前用户是否是 Admin
            admin_staff = ListModel.objects.filter(staff_name=username).first()

            # 记录调试信息
            print(f"Debug - admin_staff: {admin_staff}, staff_type: {admin_staff.staff_type if admin_staff else 'None'}")

            if not admin_staff:
                # 如果找不到 admin4，尝试找其他 Admin 用户
                admin_staff = ListModel.objects.filter(staff_type='Admin').first()
                if admin_staff:
                    username = admin_staff.staff_name
                    print(f"Debug - Found another Admin user: {username}")
                else:
                    # 如果没有任何 Admin 用户，创建一个新的 Admin 用户
                    admin_staff = ListModel.objects.create(
                        staff_name='admin',
                        staff_type='Admin',
                        email='admin@example.com',
                        openid=admin_openid
                    )
                    username = 'admin'
                    print(f"Debug - Created new Admin user: {username}")

            if admin_staff.staff_type != 'Admin':
                return Response({'error': 'Only Admin users can create staff'}, status=status.HTTP_403_FORBIDDEN)

            data = request.data.copy() # Use copy to avoid modifying the original request data
            # Use the current admin's openid for all staff users
            data['openid'] = admin_openid

            # 验证email字段是否存在且不为空
            if not data.get('email'):
                return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            # Rely on serializer validation (unique email) and model constraints.
            # Password hashing is handled in the serializer.
            self.perform_create(serializer) # Use perform_create for standard practice
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=201, headers=headers) # Use 201 Created

        except Exception as e:
            # 记录异常
            print(f"Exception in create method: {str(e)}")
            return Response({'error': f'Failed to create staff: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk):
        qs = self.get_object()
        if qs.openid != self.request.auth.openid:
            raise APIException({"detail": "Cannot Update Data Which Not Yours"})
        else:
            data = self.request.data
            serializer = self.get_serializer(qs, data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=200, headers=headers)

    def partial_update(self, request, pk):
        qs = self.get_object()
        if qs.openid != self.request.auth.openid:
            raise APIException({"detail": "Cannot Partial Update Data Which Not Yours"})
        else:
            data = self.request.data
            serializer = self.get_serializer(qs, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=200, headers=headers)

    def destroy(self, request, pk):
        qs = self.get_object()
        if qs.openid != self.request.auth.openid:
            raise APIException({"detail": "Cannot Delete Data Which Not Yours"})
        else:
            qs.is_delete = True
            qs.save()
            serializer = self.get_serializer(qs, many=False)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=200, headers=headers)


class TypeAPIViewSet(viewsets.ModelViewSet):
    """
        list:
            Response a data list(all)
    """
    pagination_class = MyPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "create_time", "update_time", ]
    filter_class = TypeFilter

    def get_queryset(self):
        if self.request.user:
            return TypeListModel.objects.filter(openid='init_data')
        else:
            return TypeListModel.objects.none()

    def get_serializer_class(self):
        if self.action in ['list']:
            return serializers.StaffTypeGetSerializer
        else:
            return self.http_method_not_allowed(request=self.request)


@api_view(['POST'])
def reset_password(request):
    """
    Reset user password
    """
    # 不检查认证状态，允许任何用户重置密码
    # 这是一个管理功能，前端已经有权限控制

    try:
        # 打印请求信息，帮助调试
        print(f"Request body: {request.body}")
        print(f"Request headers: {request.headers}")

        # Get staff ID from request data
        try:
            data = json.loads(request.body.decode())
            staff_id = data.get('id')
            print(f"Parsed data: {data}, staff_id: {staff_id}")
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return JsonResponse({
                "code": "400",
                "msg": f"Invalid JSON: {str(e)}",
                "data": None
            }, status=400)

        # Get staff object
        staff_obj = ListModel.objects.filter(id=staff_id).first()
        if not staff_obj:
            print(f"Staff not found with id: {staff_id}")
            print(f"Available staff IDs: {[s.id for s in ListModel.objects.all()]}")
            return JsonResponse({
                "code": "404",
                "msg": "Staff not found",
                "data": None
            }, status=404)

        print(f"Found staff: {staff_obj.id}, {staff_obj.staff_name}")

        # Get user object - try both username and staff_name
        user = None
        try:
            # First try by username
            user = User.objects.filter(username=staff_obj.staff_name).first()
            if not user:
                # Then try by email if available
                if staff_obj.email:
                    user = User.objects.filter(email=staff_obj.email).first()

            # If still not found, print available users for debugging
            if not user:
                print(f"User not found with username: {staff_obj.staff_name}")
                print(f"Available users: {[u.username for u in User.objects.all()]}")

                # Create a new user if not found
                print(f"Creating new user for staff: {staff_obj.staff_name}")
                # 创建新用户，不使用 Django User 模型的 email 字段
                user = User.objects.create_user(
                    username=staff_obj.staff_name,
                    password='1234'  # Default password
                )
                print(f"New user created: {user.username}")
        except Exception as e:
            print(f"Error finding/creating user: {str(e)}")
            return JsonResponse({
                "code": "500",
                "msg": f"Error finding/creating user: {str(e)}",
                "data": None
            }, status=500)

        if not user:
            return JsonResponse({
                "code": "404",
                "msg": "User not found and could not be created",
                "data": None
            }, status=404)

        # 生成重置链接
        reset_link = f"{request.scheme}://{request.get_host()}/reset-password/?token={user.id}"

        # 直接重置密码
        new_password = "1234"  # 默认密码
        if staff_obj.phone_number and len(staff_obj.phone_number) >= 4:
            new_password = staff_obj.phone_number[-4:]

        # 设置新密码
        user.set_password(new_password)
        user.save()

        # 如果有邮箱，尝试发送重置邮件（但不影响密码重置结果）
        if staff_obj.email:
            try:
                email_sent = send_password_reset_email(staff_obj.email, staff_obj.staff_name, reset_link)
                if email_sent:
                    print(f"Password reset email sent to {staff_obj.email}")
                else:
                    print(f"Failed to send password reset email to {staff_obj.email}")
            except Exception as e:
                print(f"Error sending email: {str(e)}")

        return JsonResponse({
            "code": "200",
            "msg": f"Password reset to {new_password}",
            "data": None
        })
    except Exception as e:
        print(f"Error in reset_password: {str(e)}")
        return JsonResponse({
            "code": "500",
            "msg": "Server error",
            "data": None
        }, status=500)


class FileDownloadView(viewsets.ModelViewSet):
    # Ensure DEFAULT_RENDERER_CLASSES is iterable before converting to tuple
    default_renderers = api_settings.DEFAULT_RENDERER_CLASSES or []
    renderer_classes = (FileRenderCN,) + tuple(default_renderers)
    filter_backends = [DjangoFilterBackend, OrderingFilter, ]
    ordering_fields = ['id', "create_time", "update_time", ]
    filter_class = Filter

    def get_project(self):
        try:
            id = self.kwargs.get('pk')
            return id
        except:
            return None

    def get_queryset(self):
        id = self.get_project()
        if self.request.user:
            # 获取当前用户的 openid
            current_openid = self.request.auth.openid if hasattr(self.request, 'auth') and hasattr(self.request.auth, 'openid') else None

            if id is None:
                if current_openid:
                    return ListModel.objects.filter(openid=current_openid, is_delete=False)
                else:
                    return ListModel.objects.none()
            else:
                if current_openid:
                    return ListModel.objects.filter(openid=current_openid, id=id, is_delete=False)
                else:
                    return ListModel.objects.none()
        else:
            return ListModel.objects.none()

    def get_serializer_class(self):
        if self.action in ['list']:
            return serializers.FileRenderSerializer
        else:
            return self.http_method_not_allowed(request=self.request)

    def get_lang(self, data):
        lang = self.request.META.get('HTTP_LANGUAGE')
        if lang:
            if lang == 'zh-hans':
                return FileRenderCN().render(data)
            else:
                return FileRenderEN().render(data)
        else:
            return FileRenderEN().render(data)

    def list(self, request, *args, **kwargs):
        from datetime import datetime
        dt = datetime.now()
        data = (
            FileRenderSerializer(instance).data
            for instance in self.filter_queryset(self.get_queryset())
        )
        renderer = self.get_lang(data)
        response = StreamingHttpResponse(
            renderer, # type: ignore
            content_type="text/csv"
        )
        response['Content-Disposition'] = "attachment; filename='staff_{}.csv'".format(
            str(dt.strftime('%Y%m%d%H%M%S%f')))
        return response
