from rest_framework import serializers
from .models import ListModel, TypeListModel
from utils import datasolve
from django.contrib.auth.hashers import make_password # Import make_password

class StaffGetSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(read_only=True, required=False)
    real_name = serializers.CharField(read_only=True, required=False) # Added
    staff_type = serializers.CharField(read_only=True, required=False)
    email = serializers.EmailField(read_only=True, required=False) # Added
    phone_number = serializers.CharField(read_only=True, required=False) # Added
    # Removed check_code and openid from default view if not needed
    create_time = serializers.DateTimeField(read_only=True)
    update_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ListModel
        # Exclude password for security, keep openid/check_code excluded for now
        exclude = ['openid', 'is_delete', 'password']
        read_only_fields = ['id', ]

class StaffPostSerializer(serializers.ModelSerializer):
    # openid = serializers.CharField(read_only=False, required=False, validators=[datasolve.openid_validate]) # No longer required for creation
    staff_name = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    real_name = serializers.CharField(read_only=False, required=False, allow_blank=True) # Added, optional
    staff_type = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    email = serializers.EmailField(read_only=False, required=True) # Added, required
    phone_number = serializers.CharField(read_only=False, required=False, allow_blank=True) # Added, optional
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}) # Added, required, write-only
    # check_code = serializers.IntegerField(read_only=False, required=True, validators=[datasolve.data_validate]) # No longer required for creation

    class Meta:
        model = ListModel
        # Keep check_code and openid excluded if they are not set during creation
        exclude = ['is_delete',  'openid']
        read_only_fields = ['id', 'create_time', 'update_time', ]

    def create(self, validated_data):
        # Hash the password provided during creation.
        # The 'password' field is required=True, so it will be in validated_data.
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class StaffUpdateSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    real_name = serializers.CharField(read_only=False, required=False, allow_blank=True) # Added
    staff_type = serializers.CharField(read_only=False, required=True, validators=[datasolve.data_validate])
    email = serializers.EmailField(read_only=False, required=False) # Added, optional on update? Assume yes for now.
    phone_number = serializers.CharField(read_only=False, required=False, allow_blank=True) # Added
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'}) # Added, optional, write-only

    class Meta:
        model = ListModel
        # Exclude fields not typically updated this way
        exclude = ['openid', 'is_delete']
        read_only_fields = ['id', 'create_time', 'update_time', ]

    def update(self, instance, validated_data):
        # Hash password if it is being updated
        password = validated_data.pop('password', None)
        if password:
            instance.password = make_password(password)
        return super().update(instance, validated_data)


class StaffPartialUpdateSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    real_name = serializers.CharField(read_only=False, required=False, allow_blank=True) # Added
    staff_type = serializers.CharField(read_only=False, required=False, validators=[datasolve.data_validate])
    email = serializers.EmailField(read_only=False, required=False) # Added
    phone_number = serializers.CharField(read_only=False, required=False, allow_blank=True) # Added
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'}) # Added, optional, write-only

    class Meta:
        model = ListModel
        # Exclude fields not typically updated this way
        exclude = ['openid', 'is_delete']
        read_only_fields = ['id', 'create_time', 'update_time', ]

    def update(self, instance, validated_data):
        # Hash password if it is being updated
        password = validated_data.pop('password', None)
        if password:
            instance.password = make_password(password)
        return super().update(instance, validated_data)

class FileRenderSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(read_only=False, required=False)
    real_name = serializers.CharField(read_only=False, required=False) # Added
    staff_type = serializers.CharField(read_only=False, required=False)
    email = serializers.EmailField(read_only=False, required=False) # Added
    phone_number = serializers.CharField(read_only=False, required=False) # Added
    create_time = serializers.DateTimeField(read_only=True)
    update_time = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ListModel
        ref_name = 'StaffFileRenderSerializer'
        # Exclude sensitive/internal fields
        exclude = ['openid', 'is_delete', 'password']

class StaffTypeGetSerializer(serializers.ModelSerializer):
    staff_type = serializers.CharField(read_only=True, required=False)
    creater = serializers.CharField(read_only=True, required=False)
    create_time = serializers.DateTimeField(read_only=True)
    update_time = serializers.DateTimeField(read_only=True)
    class Meta:
        model = TypeListModel
        exclude = ['openid']
        read_only_fields = ['id', ]
