from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password, check_password
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
        required_fields = ['staff_name', 'email', 'password', 'staff_type']
        for field in required_fields:
            if field not in data:
                return Response({'error': f'{field} is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查用户名和邮箱是否已存在
        if ListModel.objects.filter(staff_name=data['staff_name']).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        if ListModel.objects.filter(email=data['email']).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建用户
        user = ListModel(
            staff_name=data['staff_name'],
            email=data['email'],
            password=make_password(data['password']),
            staff_type=data['staff_type'],
            real_name=data.get('real_name', ''),
            phone_number=data.get('phone_number', ''),
            check_code=random.randint(1000, 9999)
        )
        user.save()
        
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)


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
    """
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
            if id is None:
                return ListModel.objects.filter(openid=self.request.auth.openid, is_delete=False)
            else:
                return ListModel.objects.filter(openid=self.request.auth.openid, id=id, is_delete=False)
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
        data = request.data.copy() # Use copy to avoid modifying the original request data
        # Keep openid injection as it represents warehouse_id association
        data['openid'] = self.request.auth.openid # type: ignore
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        # Rely on serializer validation (unique email) and model constraints.
        # Password hashing is handled in the serializer.
        # The old check for staff_name uniqueness within openid is removed for now,
        # assuming email is the primary unique identifier for login.
        self.perform_create(serializer) # Use perform_create for standard practice
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers) # Use 201 Created

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
            if id is None:
                return ListModel.objects.filter(openid=self.request.auth.openid, is_delete=False)
            else:
                return ListModel.objects.filter(openid=self.request.auth.openid, id=id, is_delete=False) # type: ignore
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
